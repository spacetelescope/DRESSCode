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
from pathlib import Path
from typing import Optional, Sequence

import numpy as np
from astropy.io import fits

from dresscode.utils import check_filter, load_config


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

    # PART 1: Append all frames per filter and per type.

    # clear out the all_* files
    filters = ("um2", "uw2", "uw1")
    imgtypes = ("sk", "ex", "lss", "mk")
    [
        Path.unlink(path + "all_" + ff + "_" + tt + ".img", exist_ok=True)
        for ff in filters
        for tt in imgtypes
    ]

    file_patt_to_corr = ("sk_corr.img", "ex_corr.img", "lss_corr.img", "mk_corr.img")
    filenames = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith(file_patt_to_corr)
    ]

    print("Appending all frames...")

    for i, filename in enumerate(filenames):

        # Check the type of the image and give the image a type label.
        typelabel = check_type(filename)

        # For the mask files: make sure that also the NaN pixels in the exposure
        # maps are included in the mask as well as pixels with a very low exposure
        # time.
        if typelabel == "mk":
            update_mask(path + filename)
            filename = filename.replace(".img", "_new.img")

        # Check the filter of the image and give the image a filter label.
        filterlabel = check_filter(filename)

        # Append all frames to one "total" image.
        append(path + filename, typelabel, filterlabel, i)

    # PART 2: Co-add the frames in each "total" image.

    print("Co-adding all frames...")

    for ff in filters:
        for tt, param in (("sk", "grid"), ("ex", "expmap"), ("lss", "lssmap")):
            filename = path + f"all_{ff}_{tt}.img"
            if os.path.isfile(filename):
                coaddframes(filename, param)

    # Check the output of the uvotimsum task.
    error = False

    for filename in sorted(os.listdir(path)):

        # If the file is an output text file of uvotimsum, open the file.
        if filename.startswith("output_uvotimsum"):
            with open(path + filename, "r") as fh:
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

    # PART 3: Normalize the summed sky images.

    print("Normalizing the summed sky images...")

    if os.path.isfile(path + "sum_um2_sk.img"):
        norm(path + "sum_um2_sk.img")
    if os.path.isfile(path + "sum_uw2_sk.img"):
        norm(path + "sum_uw2_sk.img")
    if os.path.isfile(path + "sum_uw1_sk.img"):
        norm(path + "sum_uw1_sk.img")

    if error is False:
        print(
            "All frames were successfully co-added and the summed sky images were "
            "normalized."
        )

    return 0


# Functions for PART 1: Appending frames.
# Function to check the type of the image and return a type label.
def check_type(filename):
    if filename.endswith("sk_corr.img"):
        return "sk"
    elif filename.endswith("ex_corr.img"):
        return "ex"
    elif filename.endswith("lss_corr.img"):
        return "lss"
    elif filename.endswith("mk_corr.img"):
        return "mk"


# Function to update the mask with pixels that are NaN in the exposure map and pixels
# that have very low exposure times.
def update_mask(filename):
    # Open the mask file and the exposure map and copy the primary header (extension 0
    # of hdulist) to a new hdulist.
    hdulist_mk = fits.open(filename)
    hdulist_ex = fits.open(filename.replace("mk", "ex"))
    new_hdu_header = fits.PrimaryHDU(header=hdulist_mk[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    # For all frames in the mask file: Update the mask.
    for i in range(1, len(hdulist_mk)):
        new_mask = hdulist_mk[i].data * (
            np.isfinite(hdulist_ex[i].data) * hdulist_ex[i].data > 1.0
        )
        new_hdu = fits.ImageHDU(new_mask, hdulist_mk[i].header)
        new_hdulist.append(new_hdu)

    # Write the new hdulist to new mask file.
    new_hdulist.writeto(filename.replace(".img", "_new.img"))


# Function to copy the first image of a certain filter and a certain type or to append
# frames, depending on whether it is the first image or not.
def append(filename, typelabel, filterlabel, i):
    allfile = (
        os.path.dirname(filename) + "/all_" + filterlabel + "_" + typelabel + ".img"
    )

    # If the "total" image of this type and this filter does not yet exist, create it.
    if not os.path.isfile(allfile):
        shutil.copyfile(filename, allfile)

        print("File " + os.path.basename(allfile) + " has been created.")
    # Else: append the frames.
    else:
        appendframes(filename, allfile, i)


# Function to open an image and append all its frames to the "total" image.
def appendframes(filename, allfile, i):
    path = os.path.dirname(filename) + "/"

    # Count the total number of images.
    num = sum(
        4 for filename in sorted(os.listdir(path)) if filename.endswith("sk_corr.img")
    )

    hdulist = fits.open(filename)
    for j in range(1, len(hdulist)):
        infile = filename + "+" + str(j)
        totfile = allfile
        subprocess.call("ftappend " + infile + " " + totfile, cwd=path, shell=True)

        print(
            "Frame "
            + os.path.basename(infile)
            + " (frame "
            + str(j)
            + "/"
            + str(len(hdulist) - 1)
            + " of image "
            + str(i)
            + "/"
            + str(num)
            + ") appended to "
            + os.path.basename(allfile)
            + "."
        )


# Function for PART 2: Co-add frames.
# Function to co-add all frames of an image.
def coaddframes(allfile, method):
    path = os.path.dirname(allfile) + "/"

    # Specify the output file, the mask file and the terminal output file.
    outfile = allfile.replace("all", "sum")
    maskfile = allfile.rsplit("_", 1)[0] + "_mk.img"
    terminal_output_file = (
        path + "output_uvotimsum" + allfile.split("ll")[1].split(".")[0] + ".txt"
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


# Function for PART 3: Normalizing images.
# Function to normalize an image.
def norm(filename):
    path = os.path.dirname(filename) + "/"

    # Specify the input files and the output file.
    infil1 = filename + "+1"
    infil2 = filename.replace("sk", "ex") + "+1"
    outfil = filename.replace("sk", "nm")

    # Run farith with the specified parameters:
    subprocess.call(
        "farith infil1="
        + infil1
        + " infil2="
        + infil2
        + " outfil="
        + outfil
        + " ops=div null=y",
        cwd=path,
        shell=True,
    )

    print(os.path.basename(filename) + " has been normalized.")


if __name__ == "__main__":
    exit(main())
