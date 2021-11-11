#!/usr/bin/env python3

"""
collect_images.py: Script to collect all raw files needed in the data reduction.
"""


import os
import shutil
from argparse import ArgumentParser
from typing import Optional, Sequence

from dresscode.utils import listdir_nohidden, load_config


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="path to config.txt", default="config.txt"
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)

    galaxy = config["galaxy"]
    path = config["path"] + galaxy

    # Define the paths of the raw data and of the new directory with raw images.
    rawpath = path + "/Raw_data/"
    topath = path + "/Raw_images/"

    # Create a new directory with all the raw UV images (*_rw.img.gz) from the uvot/image/
    # folders, the UV event files (*w1po_uf.evt.gz) from the uvot/event/ folders, the
    # attitude (*pat.fits.gz) files from the auxil/ folders and the aspect following
    # (*uaf.hk.gz) files from the uvot/hk/ folders.
    # Initialize the counters.
    raw_image_file_count = 0
    event_file_count = 0
    attitude_file_count = 0
    aspect_file_count = 0

    # Create the new directory.
    os.mkdir(topath)

    # For each subfolder in the Raw_data folder:
    for directory in listdir_nohidden(rawpath):
        # Collect the raw UV images.
        for file in listdir_nohidden(rawpath + directory + "/uvot/image/"):
            if (
                file.endswith("m2_rw.img.gz")
                or file.endswith("w1_rw.img.gz")
                or file.endswith("w2_rw.img.gz")
            ):
                shutil.copy(rawpath + directory + "/uvot/image/" + file, topath)
                raw_image_file_count += 1

        # Collect the UV event files.
        if os.path.isdir(rawpath + directory + "/uvot/event/"):
            for file in listdir_nohidden(rawpath + directory + "/uvot/event/"):
                if (
                    file.endswith("m2w1po_uf.evt.gz")
                    or file.endswith("w1w1po_uf.evt.gz")
                    or file.endswith("w2w1po_uf.evt.gz")
                ):
                    shutil.copy(rawpath + directory + "/uvot/event/" + file, topath)
                    event_file_count += 1

        # Collect the attitude files.
        for file in listdir_nohidden(rawpath + directory + "/auxil/"):
            if file.endswith("pat.fits.gz"):
                shutil.copy(rawpath + directory + "/auxil/" + file, topath)
                attitude_file_count += 1

        # Collect the aspect following files.
        for file in listdir_nohidden(rawpath + directory + "/uvot/hk/"):
            if file.endswith("uaf.hk.gz"):
                shutil.copy(rawpath + directory + "/uvot/hk/" + file, topath)
                aspect_file_count += 1

    print(
        f"{raw_image_file_count} raw image files, "
        f"{event_file_count} event files, "
        f"{attitude_file_count} attitude files and "
        f"{aspect_file_count} aspect following files have been copied to {topath}"
    )

    return 0


if __name__ == "__main__":
    exit(main())
