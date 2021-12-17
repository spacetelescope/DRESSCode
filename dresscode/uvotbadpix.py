#!/usr/bin/env python3

"""
uvotbadpix.py: Script to create quality maps.
"""

import os
import subprocess
from argparse import ArgumentParser
from typing import Optional, Sequence

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

    print("Creating quality maps...")

    # Count the total number of sky images
    sky_images = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith("sk.img") and "uat" in filename
    ]
    num = len(sky_images)
    # Initialize the error flag
    error = False

    for i, filename in enumerate(sky_images):

        # Specify the input file, the output file and the terminal output file.
        infile = filename
        outfile = "quality_" + filename.replace("sk", "badpix")
        terminal_output_file = (
            path + "output_uvotbadpix_" + filename.replace(".img", ".txt")
        )

        # Open the terminal output file and run uvotbadpix with the specified parameters:
        with open(terminal_output_file, "w") as terminal:
            subprocess.call(
                "uvotbadpix infile=" + infile + " badpixlist=CALDB outfile=" + outfile,
                cwd=path,
                shell=True,
                stdout=terminal,
            )

        # Check if the badpixel file was succesfully created.
        with open(terminal_output_file, "r") as fh:
            text = fh.read()

        # If the word "error" is encountered or if the words "created output image" are not
        # encountered, print an error message.
        if "error" in text or "created output image" not in text:
            print("An error has occurred for image " + filename)
            error = True

        print(f"Quality map created for all (other) frames of {filename} ({i+1}/{num})")

    if error is False:
        print("Quality maps were successfully created for all sky images.")

    return 0


if __name__ == "__main__":
    exit(main())
