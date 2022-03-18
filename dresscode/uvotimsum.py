#!/usr/bin/env python3

"""
uvotimsum.py: Script to co-add frames per type, per filter and per year and to normalize
the summed sky images.

Note: This script assumes that all frames have been aspect corrected, and that the files
have been separated into different directories based on their observation period (e.g.
per year).
"""

import os
import shutil
import subprocess
from argparse import ArgumentParser
from typing import Optional, Sequence

from astropy.io import fits

from dresscode.utils import check_filter, load_config, norm

# we need to primary data, coicorr, coicorr_rel, masks, and exposure maps
FILE_PATT_TO_SUM = {
    "_sk_corr_mk_nm_coi_lss_zp_dn.img": "sk",  # primary data
    "_sk_corr_mk_nm_coi_corrfactor.img": "cf",  # coincidence corr factor
    "_sk_corr_mk_nm_coi_coicorr_unc.img": "ru",  # coincidence corr relative uncertainty
    "_mk_corr_new.img": "mk",  # masks
    "_ex_corr.img": "ex",  # exposure map
}


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

    # for diff. image types, append frames to one "total" image.

    print("Appending all image frames...")
    image_files_to_sum = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith("_sk_corr_mk_nm_coi_lss_zp_dn.img")
    ]
    for i, fname in enumerate(image_files_to_sum):
        filterlabel = check_filter(fname)
        append(path + fname, "sk", filterlabel)
        print(f"Finished appending frames for image {i+1}/{len(image_files_to_sum)}.")

    print("Appending all coi corr factors...")
    # todo:
    # "coincidence loss correction factor": cannot simply be summed.
    # What we want is a weighted average of the factors (weighted by counts).
    # To achieve this, we can “undo” the correction for a moment and calculate the counts
    # as if no coincidence correction happened,
    # i.e. orig_counts = primary / corr_factor (where orig_counts is the uncorrected counts).
    # Make sure primary is in counts.
    # We can then sum all the or_counts with uvotimsum in the same way as we sum primary.
    # The weighted correction factor for the summed image is then F = summed_primary / summed_orig_counts.

    print("Appending all coi corr factors relative uncertainties...")
    # todo:
    # "coincidence loss correction uncertainty": convert the uncertainty from a relative
    # fraction to an uncertainty in counts, by multiplying the rel_unc frame with the primary frame (in counts).

    print("Appending all masks...")
    mask_files_to_sum = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith("_mk_corr_new.img")
    ]
    for i, fname in enumerate(mask_files_to_sum):
        filterlabel = check_filter(fname)
        # todo: append() possibly needs modifications
        append(path + fname, "mk", filterlabel)
        print(f"Finished appending frames for mask {i+1}/{len(image_files_to_sum)}.")

    print("Appending all exposure maps...")
    mask_files_to_sum = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith("_ex_corr.img")
    ]
    for i, fname in enumerate(mask_files_to_sum):
        filterlabel = check_filter(fname)
        # todo: append() possibly needs modifications
        append(path + fname, "ex", filterlabel)
        print(f"Finished appending frames for mask {i+1}/{len(image_files_to_sum)}.")

    # Co-add the frames in each "total" image
    print("Co-adding all frames...")

    filter_types = ["um2", "uw1", "uw1"]
    # todo: data types are incorrect
    data_types = ["data", "coicorr", "coicorr_rel"]
    for filt in filter_types:
        for data_type in data_types:
            all_fname = f"all_{filt}_sk_{data_type}.img"
            if os.path.isfile(path + all_fname):
                coaddframes(path + all_fname, "grid")

    # handle the exposure maps
    if os.path.isfile(path + "all_um2_ex.img"):
        coaddframes(path + "all_um2_ex.img", "expmap")
    if os.path.isfile(path + "all_uw2_ex.img"):
        coaddframes(path + "all_uw2_ex.img", "expmap")
    if os.path.isfile(path + "all_uw1_ex.img"):
        coaddframes(path + "all_uw1_ex.img", "expmap")

    # Check the output of the uvotimsum task.
    error = False

    output_uvotimsum_files = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.startswith("output_uvotimsum")
    ]

    for fname in output_uvotimsum_files:

        # If the file is an output text file of uvotimsum, open the file.
        with open(path + fname) as fh:
            text = fh.read()

        # If the word "error" is encountered, print an error message.
        if (
            "error" in text
            or "created output image" not in text
            or "all checksums are valid" not in text
        ):
            print(
                "An error has occurred for image all_"
                + fname.split("_")[2]
                + "_"
                + fname.split("_")[3].split(".")[0]
                + ".img"
            )
            error = True

    print("Normalizing the summed sky images...")
    # todo

    # if os.path.isfile(path + "sum_um2_sk.img"):
    #     norm(path + "sum_um2_sk.img")
    # if os.path.isfile(path + "sum_uw2_sk.img"):
    #     norm(path + "sum_uw2_sk.img")
    # if os.path.isfile(path + "sum_uw1_sk.img"):
    #     norm(path + "sum_uw1_sk.img")

    if error is False:
        print("All frames successfully co-added and the summed sky images normalized.")

    return 0


def append(filename, typelabel, filterlabel):
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

    # Count the total number of images.

    hdulist = fits.open(filename)
    for j in range(1, len(hdulist)):
        infile = filename + "+" + str(j)
        totfile = allfile
        subprocess.call(f"ftappend {infile} {totfile}", cwd=path, shell=True)

        print(
            f"Frame {os.path.basename(infile)}"
            + f" (frame {j}/{len(hdulist) - 1}) appended to {os.path.basename(allfile)}."
        )


def coaddframes(allfile, method):
    """co-add all frames of an image"""
    path = os.path.dirname(allfile) + "/"

    # Specify the output file, the mask file and the terminal output file.
    outfile = allfile.replace("all", "sum")
    maskfile = allfile.rsplit("_", 1)[0] + "_mk.img"
    terminal_output_file = (
        path + "output_uvotimsum" + allfile.split("ll")[-1].split(".")[0] + ".txt"
    )

    # Open the terminal output file and run uvotimsum with the specified parameters.
    with open(terminal_output_file, "w") as terminal:
        subprocess.call(
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
    print(
        "All frames in "
        + os.path.basename(allfile)
        + " have been co-added into "
        + os.path.basename(outfile)
        + "."
    )


if __name__ == "__main__":
    exit(main())
