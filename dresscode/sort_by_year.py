#!/usr/bin/env python3

"""sort_by_year.py: Script to sort the files in working_dir by year
Reads header info from *rw.img files to identify the year
Creates the year directory if it doesn't exist
Then moves the rw.img file as well as any derivatives into the year
folder
"""

import os
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional, Sequence

from astropy.io import fits

from dresscode.utils import load_config


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="path to config.txt", default="config.txt"
    )
    parser.add_argument("--dryrun", action="store_true", help="dry run flag")
    args = parser.parse_args(argv)

    config = load_config(args.config)

    # Specify the galaxy and the path to the raw images.
    galaxy = config["galaxy"]
    path = config["path"] + galaxy + "/Raw_images/"
    working_path = config["path"] + galaxy + "/working_dir/"

    # Print titles of columns.
    print("filename\t\t\t#frames\tfilter\tdate\n")

    raw_images = [
        filename for filename in sorted(os.listdir(path)) if filename.endswith("rw.img")
    ]

    for filename in raw_images:

        # Open the image, calculate the number of individual frames in the image.
        hdulist = fits.open(path + filename)
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
        target_path = Path(f"{working_path}/{file_year}")
        target_path.mkdir(parents=True, exist_ok=True)

        # move files into year directory
        match_str = filename[:13]
        data_files = set(Path(working_path).glob(f"*{match_str}*"))
        for data_file in data_files:
            if args.dryrun:
                print(f"moving {data_file} to {target_path / data_file.name}")
            else:
                data_file.rename(target_path / data_file.name)

    return 0


if __name__ == "__main__":
    exit(main())
