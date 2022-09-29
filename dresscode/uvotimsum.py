#!/usr/bin/env python3

"""
uvotimsum.py: Script to co-add frames per type, per filter and per year and to normalize
the summed sky images.

Note: This script assumes that all frames have been aspect corrected, and that the files
have been separated into different directories based on their observation period (e.g.
per year).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Sequence

import numpy as np
from astropy.io import fits

from dresscode.utils import check_filter, load_config, norm


@dataclass(frozen=True)
class FilePatternItem:
    name: str = ""
    in_file_pattern: str = ""
    out_file_type: str = ""
    uvotimsum_method: str | None = None


# we need to sum primary data, coicorr, coicorr_rel, masks, and exposure maps for each filter
FILTER_TYPES = ["um2", "uw2", "uw1"]
FILE_TYPES_TO_SUM = [
    # masks need to be appended so that they can be used during the co-addition step for the images but aren't summed
    FilePatternItem(
        name="mask",
        in_file_pattern="_mk_corr_new.img",
        out_file_type="mk",
    ),
    FilePatternItem(
        name="exposure map",
        in_file_pattern="_ex_corr.img",
        out_file_type="ex",
        uvotimsum_method="expmap",
    ),
    FilePatternItem(
        name="primary image",
        in_file_pattern="_sk_corr_coi_lss_zp_dn.img",
        out_file_type="data",
        uvotimsum_method="grid",
    ),
    FilePatternItem(
        name="original counts",
        in_file_pattern="_sk_corr_coi_lss_zp_dn_oc.img",
        out_file_type="orig_counts",
        uvotimsum_method="grid",
    ),
    FilePatternItem(
        name="coi corr factors relative uncertainty",
        in_file_pattern="_sk_corr_coicorr_unc_sq_cts.img",
        out_file_type="coicorr_rel_sq",
        uvotimsum_method="grid",
    ),
    FilePatternItem(
        name="zero point corr factor in count",
        in_file_pattern="_sk_corr_zp_cts.img",
        out_file_type="zp_corr_cts",
        uvotimsum_method="grid",
    ),
]


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="path to config.txt", default="config.txt"
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)
    # Specify the galaxy and the path to the working directory.
    galaxy = config["galaxy"]
    path = config["path"] + galaxy + "/working_dir/"

    # clear out the all / sum images
    for img_type in ["all", "sum"]:
        fname_pattern = f"{img_type}_*.img"
        [Path.unlink(f, missing_ok=True) for f in Path(path).glob(fname_pattern)]

    # for diff. image types, append frames to one "all" image.
    for filetype in FILE_TYPES_TO_SUM:
        print(f"Appending all {filetype.name} files...")
        files_to_append = [
            filename
            for filename in sorted(os.listdir(path))
            if filename.endswith(filetype.in_file_pattern)
            and not filename.startswith(".")
        ]
        for i, fname in enumerate(files_to_append):
            filterlabel = check_filter(fname)
            all_fname = f"{path}/all_{filterlabel}_{filetype.out_file_type}.img"
            append_frames(path + fname, all_fname)
            print(
                f"Finished appending frames for {filetype.name} {i+1}/{len(files_to_append)}."
            )

    # Co-add the frames in each "total" image

    any_error = False
    for filetype in FILE_TYPES_TO_SUM:
        if filetype.uvotimsum_method is None:
            # skip the mask files, since we don't need to sum those
            continue

        print(f"Co-adding all frames of type {filetype.out_file_type}...")
        for filt in FILTER_TYPES:
            all_fname = f"{path}all_{filt}_{filetype.out_file_type}.img"
            out_fname = all_fname.replace("all", "sum")
            mask_fname = all_fname.rsplit(f"_{filt}_", 1)[0] + f"_{filt}_mk.img"
            if os.path.isfile(all_fname):
                error = coaddframes(
                    all_fname, mask_fname, out_fname, filetype.uvotimsum_method
                )
                any_error = any_error | error

    # the actual weighted summed corr factor is: F = summed_primary / summed_orig_counts
    # open the summed primary image and divide by the summed original counts image
    print("Calculating weighted summed corr factors...")
    for filt in FILTER_TYPES:
        primary_counts_sum_fname = f"{path}sum_{filt}_data.img"
        orig_counts_sum_fname = f"{path}sum_{filt}_orig_counts.img"
        if os.path.isfile(primary_counts_sum_fname) and os.path.isfile(
            orig_counts_sum_fname
        ):
            calc_summed_corr_factor(primary_counts_sum_fname, orig_counts_sum_fname)

    print("Calculating coincidence loss correction uncertainty...")
    for filt in FILTER_TYPES:
        coicorr_unc_sq_sum_fname = f"{path}sum_{filt}_coicorr_rel_sq.img"
        primary_counts_sum_fname = f"{path}sum_{filt}_data.img"
        if os.path.isfile(coicorr_unc_sq_sum_fname):
            calc_coicorr_uncertainty(coicorr_unc_sq_sum_fname, primary_counts_sum_fname)

    print("Calculating zero point correction factor...")
    for filt in FILTER_TYPES:
        primary_counts_sum_fname = f"{path}sum_{filt}_data.img"
        zp_corr_sum_fname = f"{path}sum_{filt}_zp_corr_cts.img"
        if os.path.isfile(zp_corr_sum_fname) and os.path.isfile(
            primary_counts_sum_fname
        ):
            calc_zp_corr_factor(zp_corr_sum_fname, primary_counts_sum_fname)

    print("Normalizing primary image counts by their exposure times...")
    for filt in FILTER_TYPES:
        sum_fname = f"{path}sum_{filt}_data.img"
        expmap_sumfile = sum_fname.replace("_data.img", "_ex.img")
        out_fname = sum_fname.replace("_data.img", "_nm.img")
        if os.path.isfile(sum_fname) and os.path.isfile(expmap_sumfile):
            with fits.open(sum_fname) as sum_hdu, fits.open(
                expmap_sumfile
            ) as expmap_sum_hdu:
                norm(sum_hdu, expmap_sum_hdu, out_fname)

    # combine into a single file for each filter
    print("Saving combined images...")
    for filt in FILTER_TYPES:
        primary_fname = f"{path}sum_{filt}_nm.img"
        coicorr_factor_fname = f"{path}sum_{filt}_coicorr_factor.img"
        coicorr_unc_fname = f"{path}sum_{filt}_coicorr_unc.img"
        zp_corr_factor_fname = f"{path}sum_{filt}_zp_corr_factor.img"
        primary_cts_fname = f"{path}sum_{filt}_data.img"

        if (
            os.path.isfile(primary_fname)
            and os.path.isfile(coicorr_factor_fname)
            and os.path.isfile(coicorr_unc_fname)
            and os.path.isfile(zp_corr_factor_fname)
            and os.path.isfile(primary_cts_fname)
        ):
            with fits.open(primary_fname) as primary_hdul, fits.open(
                coicorr_factor_fname
            ) as coicorr_hdul, fits.open(coicorr_unc_fname) as coi_unc_hdul, fits.open(
                zp_corr_factor_fname
            ) as zp_corr_hdul, fits.open(
                primary_cts_fname
            ) as primary_cts_hdul:

                primary = primary_hdul[1].data
                f_coi = coicorr_hdul[1].data
                coicorr_rel = coi_unc_hdul[1].data
                f_zp = zp_corr_hdul[1].data
                primary_cts = primary_cts_hdul[1].data

                vals = np.isfinite(primary_cts) & (primary_cts > 0)
                poisson_rel = np.full_like(primary_cts, np.nan)
                poisson_rel[vals] = 1.0 / np.sqrt(primary_cts[vals])

                header = primary_hdul[1].header
                header["PLANE0"] = "primary (counts)"
                header["PLANE1"] = "average coincidence loss correction factor"
                header[
                    "PLANE2"
                ] = "relative coincidence loss correction uncertainty (fraction)"
                header["PLANE3"] = "average zero point correction factor"
                header["PLANE4"] = "relative Poisson noise (fraction)"

                new_datacube = np.array(
                    [primary, f_coi, coicorr_rel, f_zp, poisson_rel]
                )
                sum_hdu = fits.PrimaryHDU(new_datacube, header)
                sum_hdu.writeto(path + "total_sum_" + filt + "_nm.fits", overwrite=True)

    if not any_error:
        print("All frames successfully co-added")
        return 0
    else:
        print("An error has occurred.")
        return 1


def calc_summed_corr_factor(primary_counts_sum_fname: str, orig_counts_sum_fname: str):
    """Calculate the weighted summed corr factor"""

    primary_counts_sum_hdul = fits.open(primary_counts_sum_fname)
    orig_counts_sum_hdul = fits.open(orig_counts_sum_fname)
    finite_vals = np.isfinite(primary_counts_sum_hdul[1].data) & (
        orig_counts_sum_hdul[1].data > 0
    )
    sum_coi_corr_factor = np.full_like(primary_counts_sum_hdul[1].data, np.nan)
    sum_coi_corr_factor[finite_vals] = (
        primary_counts_sum_hdul[1].data[finite_vals]
        / orig_counts_sum_hdul[1].data[finite_vals]
    )

    # todo: update the header for this data
    new_hdu_header = fits.PrimaryHDU(header=primary_counts_sum_hdul[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])
    new_hdu = fits.ImageHDU(sum_coi_corr_factor, primary_counts_sum_hdul[1].header)
    new_hdulist.append(new_hdu)
    new_fname = primary_counts_sum_fname.replace("data.img", "coicorr_factor.img")
    new_hdulist.writeto(new_fname, overwrite=True)

    primary_counts_sum_hdul.close()
    orig_counts_sum_hdul.close()


def calc_coicorr_uncertainty(
    coicorr_unc_sq_sum_fname: str, primary_counts_sum_fname: str
):
    """Calculate coincidence loss correction uncertainty"""

    coicorr_unc_sq_hdul = fits.open(coicorr_unc_sq_sum_fname)
    primary_counts_sum_hdul = fits.open(primary_counts_sum_fname)
    # this is in counts but we need to convert to fraction by dividing by corrected summed counts (primary)

    # we summed squares, square root the summed uncertainties
    new_data = np.sqrt(coicorr_unc_sq_hdul[1].data) / primary_counts_sum_hdul[1].data

    # todo: update the header for this data
    new_hdu_header = fits.PrimaryHDU(header=coicorr_unc_sq_hdul[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])
    new_hdu = fits.ImageHDU(new_data, coicorr_unc_sq_hdul[1].header)
    new_hdulist.append(new_hdu)
    new_fname = coicorr_unc_sq_sum_fname.replace(
        "coicorr_rel_sq.img", "coicorr_unc.img"
    )
    new_hdulist.writeto(new_fname, overwrite=True)

    coicorr_unc_sq_hdul.close()


def calc_zp_corr_factor(zp_corr_sum_fname: str, primary_counts_sum_fname: str):
    """Calculate the average zero point correction factor"""

    # todo: pass hdul instead of fname to avoid file load

    # take the summed zero point corr. factor _counts_ and convert back to a factor

    primary_counts_sum_hdul = fits.open(primary_counts_sum_fname)
    zp_corr_sum_hdul = fits.open(zp_corr_sum_fname)

    finite_vals = np.isfinite(primary_counts_sum_hdul[1].data) & (
        zp_corr_sum_hdul[1].data > 0
    )
    sum_zp_corr_factor = np.full_like(zp_corr_sum_hdul[1].data, np.nan)
    sum_zp_corr_factor[finite_vals] = (
        zp_corr_sum_hdul[1].data[finite_vals]
        / primary_counts_sum_hdul[1].data[finite_vals]
    )

    # todo: update the header for this data
    new_hdu_header = fits.PrimaryHDU(header=zp_corr_sum_hdul[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])
    new_hdu = fits.ImageHDU(sum_zp_corr_factor, zp_corr_sum_hdul[1].header)
    new_hdulist.append(new_hdu)
    new_fname = zp_corr_sum_fname.replace("_zp_corr_cts.img", "_zp_corr_factor.img")
    new_hdulist.writeto(new_fname, overwrite=True)

    primary_counts_sum_hdul.close()
    zp_corr_sum_hdul.close()


def append_frames(fname: str, all_fname: str):
    """Copy the first image of a filter and type into new image
    OR append frames, depending on whether it is the first image or not"""

    # If the "total" image of this type and this filter does not yet exist, create it.
    if not os.path.isfile(all_fname):
        shutil.copyfile(fname, all_fname)
        print(f"File {os.path.basename(all_fname)} has been created.")
    else:
        path = os.path.dirname(fname) + "/"

        with fits.open(fname) as hdulist:
            for j in range(1, len(hdulist)):
                infile = f"{fname}+{j}"
                subprocess.call(f"ftappend {infile} {all_fname}", cwd=path, shell=True)

                print(
                    f"Frame {os.path.basename(infile)} (frame {j}/{len(hdulist) - 1}) "
                    f"appended to {os.path.basename(all_fname)}."
                )


def coaddframes(allfile: str, maskfile: str, outfile: str, method: str) -> bool:
    """co-add all frames of an image

    Returns a bool indicating if an error occurred"""
    path = os.path.dirname(allfile) + "/"

    # Specify the output file, the mask file and the terminal output file.
    terminal_output_file = (
        path + "output_uvotimsum" + allfile.split("ll")[-1].split(".")[0] + ".txt"
    )

    # Open the terminal output file and run uvotimsum with the specified parameters.
    with open(terminal_output_file, "w") as terminal:
        ret_code = subprocess.call(
            "uvotimsum infile="
            + allfile
            + " outfile="
            + outfile
            + " method="
            + method
            + " pixsize=0.00027888888381462 exclude=DEFAULT maskfile="
            + maskfile,
            cwd=path,
            shell=True,
            stdout=terminal,
        )

    # error checking
    with open(terminal_output_file) as fh:
        text = fh.read()
    if (
        ret_code != 0
        or "error" in text
        or "created output image" not in text
        or "all checksums are valid" not in text
    ):
        print(f"An error has occurred in creating {allfile}")
        print(f"See {terminal_output_file} for more information")
        return True
    else:
        print(
            f"All frames in {os.path.basename(allfile)} have been co-added into {os.path.basename(outfile)}."
        )
        return False


if __name__ == "__main__":
    exit(main())
