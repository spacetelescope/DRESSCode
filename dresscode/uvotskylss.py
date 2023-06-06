#!/usr/bin/env python3

"""
uvotskylss.py: Script to create large scale sensitivity maps, using the updated
attitude file and after the aspect correction.
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

    print("Creating large scale sensitivity maps...")

    # Count the total number of corrected sky images. Initialize the error flag
    corr_sky_images = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith("sk_corr.img")
    ]
    num = len(corr_sky_images)
    error = False

    for i, filename in enumerate(corr_sky_images):
        # Specify the input file, the output file, the attitude file and the terminal output
        # file.
        infile = filename
        outfile = filename.replace("sk", "lss")
        attfile = filename.split("_", 1)[0] + "uat.fits"
        terminal_output_file = (
            path + "output_uvotskylss_" + filename.replace(".img", ".txt")
        )

        # Open the terminal output file and run uvotskylss with the specified parameters:
        with open(terminal_output_file, "w") as terminal:
            subprocess.call(
                "uvotskylss infile="
                + infile
                + " outfile="
                + outfile
                + " attfile="
                + attfile,
                cwd=path,
                shell=True,
                stdout=terminal,
            )

        # Check if the lss map was successfully created.
        with open(terminal_output_file) as fh:
            text = fh.read()

        # If the word "error" is encountered, print an error message.
        if "error" in text:
            print("An error has occurred for image " + filename)
            error = True

        print(
            f"Large scale sensitivity map created for all (other) frames of {filename} ({i+1}/{num})"
        )

    if error is False:
        print(
            "Large scale sensitivity maps were successfully created for all sky images."
        )

    return 0


if __name__ == "__main__":
    exit(main())
