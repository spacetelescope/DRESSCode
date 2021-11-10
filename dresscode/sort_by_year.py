#!/usr/bin/env python3

"""sort_by_year.py: Script to sort the files in working_dir by year
Reads header info from *rw.img files to identify the year
Creates the year directory if it doesn't exist
Then moves the rw.img file as well as any derivatives into the year
folder
"""

import argparse
import os
from pathlib import Path
from typing import Optional, Sequence

import configloader
from astropy.io import fits

CONFIG = configloader.load_config()

# Specify the galaxy and the path to the raw images.
GALAXY = CONFIG["galaxy"]
PATH = CONFIG["path"] + GALAXY + "/Raw_images/"
WORKING_PATH = CONFIG["path"] + GALAXY + "/working_dir/"


def main(argv: Optional[Sequence[str]] = None) -> int:
    # Print titles of columns.
    print("filename\t\t\t#frames\tfilter\tdate\n")

    for filename in sorted(os.listdir(PATH)):
        parser = argparse.ArgumentParser()
        parser.add_argument("--dryrun", action="store_true", help="dry run flag")
        args = parser.parse_args(argv)

        # If the file is not a raw image file, skip this file and continue with the next.
        if not filename.endswith("rw.img"):
            continue

        # Open the image, calculate the number of individual frames in the image.
        hdulist = fits.open(PATH + filename)
        number_of_frames = len(hdulist) - 1

        file_year = hdulist[0].header["DATE-OBS"].split("T")[0][:4]

        # Print relevant header information.
        print(
            filename
            + "\t"
            + "\t"
            + str(number_of_frames)
            + "\t"
            + hdulist[0].header["FILTER"]
            + "\t"
            + hdulist[0].header["DATE-OBS"].split("T")[0]
        )

        # get or create directory for year
        target_path = Path(f"{WORKING_PATH}/{file_year}")
        target_path.mkdir(parents=True, exist_ok=True)

        # move files into year directory
        match_str = filename[:13]
        data_files = set(Path(WORKING_PATH).glob(f"*{match_str}*"))
        for data_file in data_files:
            if args.dryrun:
                print(f"moving {data_file} to {target_path / data_file.name}")
            else:
                data_file.rename(target_path / data_file.name)

    return 0


if __name__ == "__main__":
    exit(main())
