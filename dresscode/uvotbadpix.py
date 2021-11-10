#!/usr/bin/env python3

"""
uvotbadpix.py: Script to create quality maps.
"""

import os
import subprocess
from typing import Optional, Sequence

import configloader

CONFIG = configloader.load_config()

# Specify the galaxy and the path to the working directory.
GALAXY = CONFIG["galaxy"]
PATH = CONFIG["path"] + GALAXY + "/working_dir/"


def main(argv: Optional[Sequence[str]] = None) -> int:
    print("Creating quality maps...")

    # Count the total number of sky images
    num = sum(
        1
        for filename in sorted(os.listdir(PATH))
        if filename.endswith("sk.img") and "uat" in filename
    )
    # Initialize the error flag
    error = False

    # For all files in the working directory:
    for i, filename in enumerate(sorted(os.listdir(PATH))):

        # If the file is not a sky image (created with the uat attitude file), skip this
        # file & continue with the next file.
        if not filename.endswith("sk.img") or "uat" not in filename:
            continue

        # Specify the input file, the output file and the terminal output file.
        infile = filename
        outfile = "quality_" + filename.replace("sk", "badpix")
        terminal_output_file = (
            PATH + "output_uvotbadpix_" + filename.replace(".img", ".txt")
        )

        # Open the terminal output file and run uvotbadpix with the specified parameters:
        with open(terminal_output_file, "w") as terminal:
            subprocess.call(
                "uvotbadpix infile=" + infile + " badpixlist=CALDB outfile=" + outfile,
                cwd=PATH,
                shell=True,
                stdout=terminal,
            )

        # Check if the badpixel file was succesfully created.
        file = open(terminal_output_file, "r")
        text = file.read()

        # If the word "error" is encountered or if the words "created output image" are not
        # encountered, print an error message.
        if "error" in text or "created output image" not in text:
            print("An error has occurred for image " + filename)
            error = True

        print(f"Quality map created for all (other) frames of {filename} ({i}/{num})")

    if error is False:
        print("Quality maps were successfully created for all sky images.")

    return 0


if __name__ == "__main__":
    exit(main())
