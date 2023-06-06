#!/usr/bin/env python3

"""
header_info.py: Script to print relevant information about the image files.
"""


import os
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

    # Specify the galaxy and the path to the raw images.
    galaxy = config["galaxy"]
    path = config["path"] + galaxy + "/Raw_images/"

    # Print titles of columns.
    print("filename\t\t\t#frames\tfilter\tdate\n")

    for filename in sorted(os.listdir(path)):
        # If the file is not a raw image file, skip this file and continue with the next
        # file.
        if not filename.endswith("rw.img"):
            continue

        # Open the image, calculate the number of individual frames in the image. Print
        # relevant header information.
        hdulist = fits.open(path + filename)
        number_of_frames = len(hdulist) - 1
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

        # For all frames in the image: print the datamode and calculate the total exposure
        # time.
        print("\t" + "frame" + "\t" + "datamode")
        exptime = 0.0
        for i in range(1, len(hdulist)):
            exptime += hdulist[i].header["EXPOSURE"]
            print(
                "\t"
                + str(i)
                + "\t"
                + hdulist[i].header["DATAMODE"]
                + "\t"
                + "\t"
                + str(hdulist[i].header["NAXIS1"])
                + "\t"
                + str(hdulist[i].header["NAXIS2"])
            )
        print("Total exposure time: " + str(exptime))
        print("\n")

    return 0


if __name__ == "__main__":
    exit(main())
