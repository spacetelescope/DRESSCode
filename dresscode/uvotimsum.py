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

FILE_PATT_TO_SUM = {
    "_sk_corr_coi_lss_zp_data.img": "sk",
    "_sk_corr_coi_lss_zp_coicorr.img": "sk",
    "_sk_corr_coi_lss_zp_coicorr_rel.img": "sk",
    "_mk_corr.img": "mk",
    "_ex_corr.img": "ex",
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

    files_to_sum = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith(tuple(FILE_PATT_TO_SUM.keys()))
    ]

    # Append all frames per filter and per type.

    print("Appending all frames...")

    for i, filename in enumerate(files_to_sum):

        # Check the type of the image and give the image a type label.
        typelabel = check_type(filename)

        if typelabel is None:
            continue

        # For the mask files: make sure that also the NaN pixels in the exposure
        # maps are included in the mask as well as pixels with a very low exposure
        # time.
        if typelabel == "mk":
            update_mask(path + filename)
            filename = filename.replace(".img", "_new.img")

        # Check the filter of the image and give the image a filter label.
        filterlabel = check_filter(filename)

        corr_type = check_corr_type(filename)

        # Append all frames to one "total" image.
        append(path + filename, typelabel, filterlabel, corr_type)

        print(f"Finished appending frames for image {i+1}/{len(files_to_sum)}.")

    # Co-add the frames in each "total" image.

    print("Co-adding all frames...")

    filter_types = ["um2", "uw1", "uw1"]
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

    for filename in output_uvotimsum_files:

        # If the file is an output text file of uvotimsum, open the file.
        with open(path + filename) as fh:
            text = fh.read()

        # If the word "error" is encountered, print an error message.
        if (
            "error" in text
            or "created output image" not in text
            or "all checksums are valid" not in text
        ):
            print(
                "An error has occurred for image all_"
                + filename.split("_")[2]
                + "_"
                + filename.split("_")[3].split(".")[0]
                + ".img"
            )
            error = True

    # Normalize the summed sky images.

    print("Normalizing the summed sky images...")

    if os.path.isfile(path + "sum_um2_sk.img"):
        norm(path + "sum_um2_sk.img")
    if os.path.isfile(path + "sum_uw2_sk.img"):
        norm(path + "sum_uw2_sk.img")
    if os.path.isfile(path + "sum_uw1_sk.img"):
        norm(path + "sum_uw1_sk.img")

    if error is False:
        print("All frames successfully co-added and the summed sky images normalized.")

    return 0


def check_type(filename):
    """check the type of the image and return a type label"""
    for file_patt, filetype in FILE_PATT_TO_SUM.items():
        if filename.endswith(file_patt):
            return filetype


def check_corr_type(filename: str) -> Optional[str]:
    """check whether this is:
    - primary data (counts)
    - coincidence loss correction factor
    - relative coincidence loss correction
    """

    if filename.endswith("_coicorr_rel.img"):
        return "coicorr_rel"
    elif filename.endswith("_coicorr.img"):
        return "coicorr"
    elif filename.endswith("_data.img"):
        return "data"


def append(filename, typelabel, filterlabel, corr_type):
    """Copy the first image of a filter and type into new image
    OR append frames, depending on whether it is the first image or not"""

    if corr_type is None:
        corr_type_str = ""
    else:
        corr_type_str = "_" + corr_type

    allfile = (
        f"{os.path.dirname(filename)}/all_{filterlabel}_{typelabel}{corr_type_str}.img"
    )

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
