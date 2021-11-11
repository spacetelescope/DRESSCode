#!/usr/bin/env python3

"""
uvotattcorr.py: Script to adjust the attitude file with information from the aspect
corrections.
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

    print("Adjusting the attitude files...")

    # Count the total number of attitude files.
    num = sum(
        1 for filename in sorted(os.listdir(path)) if filename.endswith("pat.fits")
    )
    # Initialize the error flag.
    error = False

    # For all files in the working directory:
    for i, filename in enumerate(sorted(os.listdir(path))):

        # If the file is not an attitude file, skip this file & continue with the next
        # file
        if not filename.endswith("pat.fits"):
            continue

        # Check for which filters there is an aspect correction file.
        filters = []
        if os.path.isfile(
            path + filename.replace("pat.fits", "_img_um2_aspcorr.ALL")
        ) or os.path.isfile(
            path + filename.replace("pat.fits", "_evt_um2_aspcorr.ALL")
        ):
            filters.append("um2")
        if os.path.isfile(
            path + filename.replace("pat.fits", "_img_uw2_aspcorr.ALL")
        ) or os.path.isfile(
            path + filename.replace("pat.fits", "_evt_uw2_aspcorr.ALL")
        ):
            filters.append("uw2")
        if os.path.isfile(
            path + filename.replace("pat.fits", "_img_uw1_aspcorr.ALL")
        ) or os.path.isfile(
            path + filename.replace("pat.fits", "_evt_uw1_aspcorr.ALL")
        ):
            filters.append("uw1")

        # Combine the correction files of the different filters into a single file.
        # Take the IMAGE based correction file if it exists, otherwise take the EVENT
        # based correction file. In case both exist, the IMAGE based one is used, for
        # simplicity.
        if len(filters) == 1:
            if os.path.isfile(
                path
                + filename.replace("pat.fits", "_img_" + filters[0] + "_aspcorr.ALL")
            ):
                corrfile = path + filename.replace(
                    "pat.fits", "_img_" + filters[0] + "_aspcorr.ALL"
                )
            else:
                corrfile = path + filename.replace(
                    "pat.fits", "_evt_" + filters[0] + "_aspcorr.ALL"
                )
        elif len(filters) == 2 or len(filters) == 3:
            if os.path.isfile(
                path
                + filename.replace("pat.fits", "_img_" + filters[0] + "_aspcorr.ALL")
            ):
                infile = path + filename.replace(
                    "pat.fits", "_img_" + filters[0] + "_aspcorr.ALL"
                )
            else:
                infile = path + filename.replace(
                    "pat.fits", "_evt_" + filters[0] + "_aspcorr.ALL"
                )
            if os.path.isfile(
                path
                + filename.replace("pat.fits", "_img_" + filters[1] + "_aspcorr.ALL")
            ):
                pastefile = path + filename.replace(
                    "pat.fits", "_img_" + filters[1] + "_aspcorr.ALL"
                )
            else:
                pastefile = path + filename.replace(
                    "pat.fits", "_evt_" + filters[1] + "_aspcorr.ALL"
                )
            outfile = path + filename.replace("pat.fits", "_aspcorr_2filters.ALL")
            subprocess.call(
                "ftpaste infile="
                + infile
                + " pastefile="
                + pastefile
                + " outfile="
                + outfile
                + " history=yes",
                cwd=path,
                shell=True,
            )
            if len(filters) == 3:
                infile = outfile
                if os.path.isfile(
                    path
                    + filename.replace(
                        "pat.fits", "_img_" + filters[2] + "_aspcorr.ALL"
                    )
                ):
                    pastefile = path + filename.replace(
                        "pat.fits", "_img_" + filters[2] + "_aspcorr.ALL"
                    )
                else:
                    pastefile = path + filename.replace(
                        "pat.fits", "_evt_" + filters[2] + "_aspcorr.ALL"
                    )
                outfile = path + filename.replace("pat.fits", "_aspcorr_3filters.ALL")
                subprocess.call(
                    "ftpaste infile="
                    + infile
                    + " pastefile="
                    + pastefile
                    + " outfile="
                    + outfile
                    + " history=yes",
                    cwd=path,
                    shell=True,
                )
            corrfile = outfile
        else:
            print(
                "Something went wrong. "
                "There must be at least one and no more than three filters."
            )

        # Specify the input attitude file, the correction file, the output attitude file
        # and the terminal output file.
        attfile = filename
        outfile = filename.replace("pat", "uat")
        terminal_output_file = (
            path + "output_uvotattcorr_" + filename.split(".", 1)[0] + ".txt"
        )

        # Open the terminal output file and run uvotattcorr with the specified parameters:
        with open(terminal_output_file, "w") as terminal:
            subprocess.call(
                "uvotattcorr attfile="
                + attfile
                + " corrfile="
                + corrfile
                + " outfile="
                + outfile,
                cwd=path,
                shell=True,
                stdout=terminal,
            )

        # Check if the attitude file was adjusted.
        file = open(terminal_output_file, "r")

        for line in file:
            # If the word "error" is encountered, print an error message.
            if "error" in line:
                print("An error has occurred for attitude file " + filename)
                error = True

        print(f"Attitude file {filename} has been adjusted ({i}/{num})")

    if error is False:
        print("All attitude files have been adjusted.")

    return 0


if __name__ == "__main__":
    exit(main())
