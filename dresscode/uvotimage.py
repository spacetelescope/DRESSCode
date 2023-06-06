#!/usr/bin/env python3

"""
uvotimage.py: Script to create sky images from raw images and event files.
"""

import os
import subprocess
from argparse import ArgumentParser
from typing import Optional, Sequence

from astropy.io import fits

from dresscode.utils import load_config


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

    print("Creating sky images...")

    # Count the total number of raw images. Initialize the error flag.
    raw_images = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith("rw.img") or filename.endswith(".evt")
    ]
    num = len(raw_images)
    error = False

    for i, filename in enumerate(raw_images):
        # Specify the input file, the prefix for the output file, the attitude file and
        # the terminal output file.
        infile = filename
        prefix = filename.split("u")[0] + "_" + filename.split(".")[1] + "_"
        attfile = filename.split("u", 1)[0] + "pat.fits"
        terminal_output_file = (
            path + "output_uvotimage_" + filename.split(".")[0] + ".txt"
        )

        # Open the file and take the RA, DEC and roll from the header.
        header = fits.open(path + filename)[0].header
        RA = header["RA_PNT"]
        DEC = header["DEC_PNT"]
        PA = header["PA_PNT"]

        # Open the terminal output file and run uvotimage with the specified parameters.
        # uvotimage help page:
        # https://heasarc.gsfc.nasa.gov/lheasoft/ftools/headas/uvotimage.html
        with open(terminal_output_file, "w") as terminal:
            subprocess.call(
                f"uvotimage infile={infile} prefix={prefix} attfile={attfile}"
                + f" teldeffile=CALDB alignfile=CALDB ra={RA} dec={DEC} roll={PA}"
                + " mod8corr=yes refattopt='ANGLE_d=5,OFFSET_s=1000'",
                cwd=path,
                shell=True,
                stdout=terminal,
            )

        # Check if the sky image was successfully created.
        with open(terminal_output_file) as file:
            for line in file:
                # If the word "error" is encountered, print an error message.
                if "error" in line:
                    print("An error has occurred for image " + filename)
                    error = True

                # If uvotimage skipped an event based image HDU, let the user know.
                if "skipping event based image HDU" in line:
                    print(line, " in file " + filename)

        print(f"Sky image created for all (other) frames of {filename} ({i+1}/{num})")

    if error is False:
        print("Sky images were successfully created for all raw images and event files")

    return 0


if __name__ == "__main__":
    exit(main())
