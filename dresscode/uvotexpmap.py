#!/usr/bin/env python3

"""
uvotexpmap2.py: Script to create exposure maps, using the updated attitude file.
"""

import os
import subprocess
from argparse import ArgumentParser
from typing import Optional, Sequence

import numpy as np
from astropy.io import fits

from dresscode.utils import load_config

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`
    import importlib_resources as pkg_resources  # type: ignore


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

    print("Creating exposure maps...")

    # Count the total number of sky images. Initialize error flag
    sky_images = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith("sk.img") and "uat" in filename
    ]
    num = len(sky_images)
    error = False

    # Open the sss masks.
    with pkg_resources.path("dresscode.sss", "sss_UV_1x1.fits") as sss_1x1_fh:
        sss_1x1 = np.ma.make_mask(fits.open(sss_1x1_fh)[0].data)
    with pkg_resources.path("dresscode.sss", "sss_UV_2x2.fits") as sss_2x2_fh:
        sss_2x2 = np.ma.make_mask(fits.open(sss_2x2_fh)[0].data)

    for i, filename in enumerate(sky_images):
        # Open the bad pixel file and copy its primary header (extension 0 of hdulist) to a
        # new hdulist.
        badpixfile = "quality_" + filename.replace("sk", "badpix")
        badpix_hdulist = fits.open(path + badpixfile)
        new_badpix_header = fits.PrimaryHDU(header=badpix_hdulist[0].header)
        new_badpix_hdulist = fits.HDUList([new_badpix_header])

        # For all frames in the bad pixel file: Update the bad pixel mask to include the sss
        # mask.
        for j in range(1, len(badpix_hdulist)):
            new_data = badpix_hdulist[j].data
            if new_data.shape == (1024, 1024):
                new_data[~sss_2x2] = 5.0
            elif new_data.shape == (2048, 2048):
                new_data[~sss_1x1] = 5.0
            else:
                print(
                    "Quality map "
                    + badpixfile
                    + "["
                    + str(j)
                    + "] does not have the correct dimensions, and cannot be combined with "
                    "an sss mask."
                )
                error = True
            new_badpix_hdu = fits.ImageHDU(new_data, badpix_hdulist[j].header)
            new_badpix_hdulist.append(new_badpix_hdu)

        # Write out the updated bad pixel file.
        new_badpix_hdulist.writeto(
            path + badpixfile.replace(".img", "_new.img"), overwrite=True
        )

        # Specify the input file, the output file, the bad pixel file, the attitude file,
        # the output mask file and the terminal output file.
        infile = filename
        outfile = filename.replace("sk", "ex")
        badpixfile = badpixfile.replace(".img", "_new.img")
        attfile = filename.split("_", 1)[0] + "uat.fits"
        maskfile = filename.replace("sk", "mk")
        trackfile = filename.split("_", 1)[0] + "uaf.hk"
        terminal_output_file = (
            path + "output_uvotexpmap_" + filename.replace(".img", ".txt")
        )

        # Open the terminal output file and run uvotexpmap with the specified parameters:
        with open(terminal_output_file, "w") as terminal:
            subprocess.call(
                "uvotexpmap infile="
                + infile
                + " badpixfile="
                + badpixfile
                + " method=SHIFTADD attfile="
                + attfile
                + " teldeffile=CALDB outfile="
                + outfile
                + " maskfile="
                + maskfile
                + " masktrim=8 trackfile="
                + trackfile
                + " attdelta=0.1 refattopt='ANGLE_d=5,OFFSET_s=1000'",
                cwd=path,
                shell=True,
                stdout=terminal,
            )

        # Check if the exposure map was successfully created.
        with open(terminal_output_file) as fh:
            text = fh.read()

        # If the word "error" is encountered or if the words "all checksums are valid" are
        # not encountered, print an error message.
        if "error" in text or "created output image" not in text:
            print("An error has occurred for image " + filename)
            error = True

        print(
            f"Exposure map created for all (other) frames of {filename} ({i+1}/{num})"
        )

    if error is False:
        print("Exposure maps were successfully created for all sky images")

    return 0


if __name__ == "__main__":
    exit(main())
