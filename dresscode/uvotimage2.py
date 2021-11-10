#!/usr/bin/env python3

"""
uvotimage2.py: Script to create sky images from raw images and event files, using
the updated attitude file.
"""


import os
import subprocess
from typing import Optional, Sequence

import configloader
from astropy.io import fits

config = configloader.load_config()

# Specify the galaxy and the path to the working directory.
galaxy = config["galaxy"]
path = config["path"] + galaxy + "/working_dir/"


def main(argv: Optional[Sequence[str]] = None) -> int:
    print("Creating sky images...")

    # Count the total number of raw images.
    num = sum(
        1
        for filename in sorted(os.listdir(path))
        if filename.endswith("rw.img")
        and "_img_" not in filename
        and "_evt_" not in filename
        or filename.endswith(".evt")
    )
    # Initialize the error flag.
    error = False

    # For all files in the working directory:
    for i, filename in enumerate(sorted(os.listdir(path))):

        # If the file is not an original raw image or an event file, skip this file and
        # continue with the next file.
        if not filename.endswith("rw.img") and not filename.endswith(".evt"):
            continue
        # Skip previously (in uvotimage.py) created raw files.
        if "_img_" in filename or "_evt_" in filename:
            continue

        # Specify the input file, the prefix for the output file, the attitude file and the
        # terminal output file.
        infile = filename
        prefix = filename.split("u")[0] + "_uat_" + filename.split(".")[1] + "_"
        attfile = filename.split("u", 1)[0] + "uat.fits"
        terminal_output_file = (
            path + "output_uvotimage_" + filename.split("_", 1)[0] + "_uat.txt"
        )

        # Open the file and take the RA, DEC and roll from the header.
        header = fits.open(path + filename)[0].header
        RA = header["RA_PNT"]
        DEC = header["DEC_PNT"]
        PA = header["PA_PNT"]

        # Open the terminal output file and run uvotimage with the specified parameters.
        with open(terminal_output_file, "w") as terminal:
            subprocess.call(
                "uvotimage infile="
                + infile
                + " prefix="
                + prefix
                + " attfile="
                + attfile
                + " teldeffile=CALDB alignfile=CALDB ra="
                + str(RA)
                + " dec="
                + str(DEC)
                + " roll="
                + str(PA)
                + " mod8corr=yes refattopt='ANGLE_d=5,OFFSET_s=1000'",
                cwd=path,
                shell=True,
                stdout=terminal,
            )

        # Check if the sky image was successfully created.
        file = open(terminal_output_file, "r")
        for line in file:
            # If the word "error" is encountered, print an error message.
            if "error" in line:
                print(
                    "An error has occurred for image "
                    + filename.rsplit("_", 1)[0]
                    + ".img"
                )
                error = True

            # If uvotimage skipped an event based image HDU, let the user know.
            if "skipping event based image HDU" in line:
                print(line, " in file " + filename)

        print(
            "Sky image created for all (other) frames of "
            + filename.rsplit("_", 1)[0]
            + f".img ({i}/{num})"
        )

    if error is False:
        print(
            "Sky images were successfully created for all raw images and event files."
        )

    return 0


if __name__ == "__main__":
    exit(main())
