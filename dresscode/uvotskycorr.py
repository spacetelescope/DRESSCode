#!/usr/bin/env python3

"""
uvotskycorr.py: Script to calculate the aspect correction.

Note: This script requires the WCSTools. Make sure this is properly installed. Most of
the time, errors occuring while running this script can be attributed to a problem with
the WCSTools.
"""


import os
import subprocess
from argparse import ArgumentParser
from typing import Optional, Sequence

from utils import load_config


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

    print("Calculating aspect corrections...")

    # Count the total number of sky images. Initialize the error flag.
    num = sum(1 for filename in sorted(os.listdir(path)) if filename.endswith("sk.img"))
    error = False

    # For all files in the working directory:
    for i, filename in enumerate(sorted(os.listdir(path))):

        # If the file is not a sky image, skip this file and continue with the next file
        if not filename.endswith("sk.img"):
            continue

        # Specify the input skyfile, the output file, the attitude file, the terminal
        # output file and the path to the catalog file.
        skyfile = filename
        outfile = filename.replace("sk.img", "aspcorr.ALL")
        attfile = filename.split("_", 1)[0] + "pat.fits"
        terminal_output_file = (
            path + "output_uvotskycorrID_" + filename.replace(".img", ".txt")
        )
        catfile = os.getcwd() + "/usnob1.spec"

        # Open the terminal output file and run uvotskycorr ID with the specified
        # parameters
        with open(terminal_output_file, "w") as terminal:
            subprocess.call(
                "uvotskycorr what=ID skyfile="
                + skyfile
                + " corrfile=NONE attfile="
                + attfile
                + " outfile="
                + outfile
                + " starid='matchtol=20 cntcorr=3 n.reference=200 n.observation=40 max.rate=1000' catspec="  # NoQA
                + catfile
                + " chatter=5",
                cwd=path,
                shell=True,
                stdout=terminal,
            )

        # Check if an aspect correction was found.
        file = open(terminal_output_file, "r")

        for line in file:
            # If the words "no correction" are encountered, print an error message.
            if "no correction" in line:
                print(
                    "!! No aspect correction found for frame "
                    + line.split()[4].replace("sk_corr", "sk")
                    + "!!"
                )
                error = True

        print(
            f"Aspect correction calculated for all (other) frames of {filename} ({i}/{num})"
        )

    if error is False:
        print(
            "Aspect corrections were successfully calculated for all frames in all sky images"
        )

    return 0


if __name__ == "__main__":
    exit(main())
