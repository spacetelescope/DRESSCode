#!/usr/bin/env python3

"""
uvotskycorr2.py: Script to calculate and apply the aspect correction, using the
updated attitude file.

Note: This script requires the WCSTools. Make sure this is properly installed. Most of
the time, errors occuring while running this script can be attributed to a problem with
the WCSTools.
"""


import os
import shutil
import subprocess
from typing import Optional, Sequence

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`
    import importlib_resources as pkg_resources  # type: ignore

import configloader

CONFIG = configloader.load_config()

# Specify the galaxy and the path to the working directory.
GALAXY = CONFIG["galaxy"]
PATH = CONFIG["path"] + GALAXY + "/working_dir/"


def main(argv: Optional[Sequence[str]] = None) -> int:
    print("Calculating and applying aspect corrections...")

    # Count the total number of sky images. Initialize the error flag.
    num = sum(
        1
        for filename in sorted(os.listdir(PATH))
        if filename.endswith("sk.img") and "uat" in filename
    )
    error = False

    for i, original_filename in enumerate(sorted(os.listdir(PATH))):

        # If the file is not a sky image (created with the uat attitude file), skip this
        # file and continue with the next file.
        if not original_filename.endswith("sk.img") or "uat" not in original_filename:
            continue

        # Copy the original file and give the copy another name. This copy will be the file
        # to work with.
        filename = original_filename.replace("sk", "sk_corr")
        shutil.copyfile(PATH + original_filename, PATH + filename)

        # Specify the input skyfile, the output file, the attitude file, the terminal output
        # file and the path to the catalog file.
        skyfile = filename
        outfile = original_filename.replace("sk.img", "aspcorr.ALL")
        attfile = original_filename.split("_", 1)[0] + "uat.fits"
        terminal_output_file = (
            PATH + "output_uvotskycorrID_" + original_filename.replace(".img", ".txt")
        )

        with pkg_resources.path(__package__, "calfiles/usnob1.spec") as catfilepath:
            catfile = str(catfilepath.absolute().resolve())

            # Open the terminal output file and run uvotskycorr ID with the specified parameters
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
                    cwd=PATH,
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
                "Aspect correction calculated for all (other) frames of "
                + original_filename
                + f" ({i}/{num})"
            )

            # Specify the correction file and the terminal output file.
            corrfile = original_filename.replace("sk.img", "aspcorr.ALL")
            terminal_output_file = (
                PATH
                + "output_uvotskycorrSKY_"
                + original_filename.replace(".img", ".txt")
            )

            # Open terminal output file and run uvotskycorr SKY with the specified parameters
            with open(terminal_output_file, "w") as terminal:
                subprocess.call(
                    "uvotskycorr what=SKY skyfile="
                    + skyfile
                    + " corrfile="
                    + corrfile
                    + " attfile="
                    + attfile
                    + " outfile=NONE catspec="
                    + catfile,
                    cwd=PATH,
                    shell=True,
                    stdout=terminal,
                )

            # Check if the aspect correction was applied.
            file = open(terminal_output_file, "r")
            text = file.read()

            # If the word "error" is encountered, print an error message.
            if "error" in text:
                print(
                    "An error has occurred during the application of the aspect correction to "
                    "image " + original_filename
                )
                error = True

            print(
                "Aspect correction applied to all (other) frames of "
                + original_filename
                + f" ({i}/{num})"
            )

            # Do the same for the corresponding exposure map.
            or_expname = original_filename.replace("sk", "ex")
            expname = or_expname.replace("ex", "ex_corr")
            shutil.copyfile(PATH + or_expname, PATH + expname)
            skyfile = expname
            terminal_output_file = (
                PATH + "output_uvotskycorrSKY_" + or_expname.replace(".img", ".txt")
            )

            with open(terminal_output_file, "w") as terminal:
                subprocess.call(
                    "uvotskycorr what=SKY skyfile="
                    + skyfile
                    + " corrfile="
                    + corrfile
                    + " attfile="
                    + attfile
                    + " outfile=NONE catspec="
                    + catfile,
                    cwd=PATH,
                    shell=True,
                    stdout=terminal,
                )

            file = open(terminal_output_file, "r")
            text = file.read()

            # If the word "error" is encountered, print an error message.
            if "error" in text:
                print(
                    "An error has occurred during the application of the aspect correction to "
                    "exposure map " + or_expname
                )
                error = True

            print(
                "Aspect correction applied to all (other) frames of "
                + or_expname
                + f" ({i}/{num})"
            )

            # Do the same for the corresponding mask file.
            or_maskname = original_filename.replace("sk", "mk")
            maskname = or_maskname.replace("mk", "mk_corr")
            shutil.copyfile(PATH + or_maskname, PATH + maskname)
            skyfile = maskname
            terminal_output_file = (
                PATH + "output_uvotskycorrSKY_" + or_maskname.replace(".img", ".txt")
            )

            with open(terminal_output_file, "w") as terminal:
                subprocess.call(
                    "uvotskycorr what=SKY skyfile="
                    + skyfile
                    + " corrfile="
                    + corrfile
                    + " attfile="
                    + attfile
                    + " outfile=NONE catspec="
                    + catfile,
                    cwd=PATH,
                    shell=True,
                    stdout=terminal,
                )

        file = open(terminal_output_file, "r")
        text = file.read()

        # If the word "error" is encountered, print an error message.
        if "error" in text:
            print(
                "An error has occurred during the application of the aspect correction to "
                "mask file " + or_maskname
            )
            error = True

        print(
            "Aspect correction applied to all (other) frames of "
            + or_maskname
            + f" ({i}/{num})"
        )

    if error is False:
        print(
            "Aspect corrections were successfully calculated and applied to all frames in "
            "all sky images, exposure maps and mask files."
        )

    return 0


if __name__ == "__main__":
    exit(main())
