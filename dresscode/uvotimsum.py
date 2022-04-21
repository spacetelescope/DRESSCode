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
from typing import Optional, Sequence

import numpy as np
from astropy.io import fits

from dresscode.utils import check_filter, load_config, norm


@dataclass(frozen=True)
class FilePatternItem:
    name: str
    data_type: str
    file_pattern: str
    uvotimsum_method: str | None


# we need to sum primary data, coicorr, coicorr_rel, masks, and exposure maps for each filter
FILTER_TYPES = ["um2", "uw2", "uw1"]
FILE_TYPES_TO_SUM = [
    # masks need to be appended so that they can be used during the co-addition step for the images but aren't summed
    FilePatternItem("mask", "mk", "_mk_corr_new.img", None),
    FilePatternItem("exposure map", "ex", "_ex_corr.img", "expmap"),
    FilePatternItem("primary image", "data", "_sk_corr_coi_lss_zp_dn.img", "grid"),
    FilePatternItem(
        "original counts", "orig_counts", "_sk_corr_coi_lss_zp_dn_oc.img", "grid"
    ),
    FilePatternItem(
        "coi corr factors relative uncertainty",
        "coicorr_rel_sq",
        "_sk_corr_coicorr_unc_sq_cts.img",
        "grid",
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

    # clear out the allfile and sum file for each filter/data type
    for filetype in FILE_TYPES_TO_SUM:
        for filter in FILTER_TYPES:
            allfname = f"{path}all_{filter}_{filetype.data_type}.img"
            if os.path.isfile(allfname):
                os.remove(allfname)
            sumfname = f"{path}sum_{filter}_{filetype.data_type}.img"
            if filetype.uvotimsum_method and os.path.isfile(sumfname):
                os.remove(sumfname)

    # for diff. image types, append frames to one "total" image.

    for filetype in FILE_TYPES_TO_SUM:
        print(f"Appending all {filetype.name} files...")
        files_to_sum = [
            filename
            for filename in sorted(os.listdir(path))
            if filename.endswith(filetype.file_pattern) and not filename.startswith(".")
        ]
        for i, fname in enumerate(files_to_sum):
            filterlabel = check_filter(fname)
            # todo: append_frames() possibly needs modifications?
            append_frames(path + fname, filetype.data_type, filterlabel)
            print(
                f"Finished appending frames for {filetype.name} {i+1}/{len(files_to_sum)}."
            )

    # Co-add the frames in each "total" image
    print("Co-adding all frames...")

    for filetype in FILE_TYPES_TO_SUM:
        for filt in FILTER_TYPES:
            if filetype.uvotimsum_method is None:
                # skip the mask files, since we don't need to sum those
                continue
            all_fname = f"{path}all_{filt}_{filetype.data_type}.img"
            out_fname = all_fname.replace("all", "sum")
            mask_fname = all_fname.rsplit(f"_{filt}_", 1)[0] + f"_{filt}_mk.img"
            if os.path.isfile(all_fname):
                ret_code = coaddframes(
                    all_fname, mask_fname, out_fname, filetype.uvotimsum_method
                )

    # the actual weighted summed corr factor is: F = summed_primary / summed_orig_counts
    # open the summed primary image and divide by the summed original counts image
    for filt in FILTER_TYPES:
        primary_counts_sum_fname = f"{path}sum_{filt}_data.img"
        orig_counts_sum_fname = f"{path}sum_{filt}_orig_counts.img"
        if os.path.isfile(primary_counts_sum_fname) and os.path.isfile(
            orig_counts_sum_fname
        ):
            primary_counts_sum_hdul = fits.open(primary_counts_sum_fname)
            orig_counts_sum_hdul = fits.open(orig_counts_sum_fname)
            sum_coi_corr_factor = (
                primary_counts_sum_hdul[0].data / orig_counts_sum_hdul[0].data
            )
            fits.writeto(
                f"{path}sum_{filt}_coicorr_factor.img",
                sum_coi_corr_factor,
                header=primary_counts_sum_hdul[0].header,
            )
            primary_counts_sum_hdul.close()
            orig_counts_sum_hdul.close()

    # "coincidence loss correction uncertainty": After the summing, take the square root
    for filt in FILTER_TYPES:
        coicorr_unc_sq_sum_fname = f"{path}sum_{filt}_coicorr_rel_sq.img"
        if os.path.isfile(coicorr_unc_sq_sum_fname):
            coicorr_unc_sq_hdul = fits.open(coicorr_unc_sq_sum_fname)
            coicorr_unc_data = np.sqrt(coicorr_unc_sq_hdul[0].data)
            fits.writeto(
                f"{path}sum_{filt}_coicorr_rel.img",
                coicorr_unc_data,
                header=coicorr_unc_sq_hdul[0].header,
            )
            coicorr_unc_sq_hdul.close()

    # normalize
    for filt in FILTER_TYPES:
        sum_fname = f"{path}sum_{filt}_data.img"
        expmap_sumfile = sum_fname.replace("data", "ex")
        out_fname = sum_fname.replace("data", "nm")
        if os.path.isfile(sum_fname) and os.path.isfile(expmap_sumfile):
            # open the files w/ astropy
            sum_hdu = fits.open(sum_fname)
            expmap_sum_hdu = fits.open(expmap_sumfile)
            norm(sum_hdu, expmap_sum_hdu, out_fname)
            sum_hdu.close()
            expmap_sum_hdu.close()

    if ret_code == 0:
        print("All frames successfully co-added")
        return 0
    else:
        print("An error has occurred.")
        return 1


def append_frames(filename, typelabel, filterlabel):
    """Copy the first image of a filter and type into new image
    OR append frames, depending on whether it is the first image or not"""

    allfile = f"{os.path.dirname(filename)}/all_{filterlabel}_{typelabel}.img"

    # If the "total" image of this type and this filter does not yet exist, create it.
    if not os.path.isfile(allfile):
        shutil.copyfile(filename, allfile)
        print(f"File {os.path.basename(allfile)} has been created.")
    else:
        appendframes(filename, allfile)


def appendframes(filename, allfile):
    """open an image and append all its frames to the "total" image"""
    path = os.path.dirname(filename) + "/"

    with fits.open(filename) as hdulist:
        for j in range(1, len(hdulist)):
            infile = f"{filename}+{j}"
            totfile = allfile
            subprocess.call(f"ftappend {infile} {totfile}", cwd=path, shell=True)

            print(
                f"Frame {os.path.basename(infile)} (frame {j}/{len(hdulist) - 1}) appended to {os.path.basename(allfile)}."
            )


def coaddframes(allfile: str, maskfile: str, outfile: str, method: str):
    """co-add all frames of an image"""
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

    error = False
    with open(terminal_output_file) as fh:
        text = fh.read()
    if (
        ret_code != 0
        or "error" in text
        or "created output image" not in text
        or "all checksums are valid" not in text
    ):
        error = True
        print(f"An error has occurred in creating {allfile}")
        print(f"See {terminal_output_file} for more information")

    if not error:
        print(
            f"All frames in {os.path.basename(allfile)} have been co-added into {os.path.basename(outfile)}."
        )
    return ret_code


if __name__ == "__main__":
    exit(main())
