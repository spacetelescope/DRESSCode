"""Sorts the files in working_dir by year
Reads header info from *rw.img files to identify the year
Creates the year directory if it doesn't exist
Then moves the rw.img file as well as any derivatives and moves them into the year folder
"""

import os
from pathlib import Path
from sys import argv

from astropy.io import fits

import configloader

# Load the configuration file.
config = configloader.load_config()

# Specify the galaxy and the path to the raw images.
galaxy = config["galaxy"]
path = config["path"] + galaxy + "/Raw_images/"
working_path = config["path"] + galaxy + "/working_dir/"

# Print titles of columns.
print(
    "filename" + "\t" + "\t" + "\t" + "#frames" + "\t" + "filter" + "\t" + "date" + "\n"
)

for filename in sorted(os.listdir(path)):

    # If the file is not a raw image file, skip this file and continue with the next file.
    if not filename.endswith("rw.img"):
        continue

    # Open the image, calculate the number of individual frames in the image. Print relevant header information.
    hdulist = fits.open(path + filename)
    number_of_frames = len(hdulist) - 1

    file_year = hdulist[0].header["DATE-OBS"].split("T")[0][:4]

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
        if len(argv) > 1 and "dryrun" in argv[1]:
            print("moving", data_file, "to", target_path / data_file.name)
        else:
            data_file.rename(target_path / data_file.name)
