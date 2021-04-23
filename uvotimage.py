""" Script to create sky images from raw images and event files. """

import os
import subprocess
from multiprocessing import Pool

from astropy.io import fits

import configloader

config = configloader.load_config()

# Specify the galaxy and the path to the working directory.
galaxy = config["galaxy"]
path = config["path"] + galaxy + "/working_dir/"


print("Creating sky images...")

# For all files in the working directory:
filenames = [
    filename
    for filename in sorted(os.listdir(path))
    if filename.endswith("rw.img") or filename.endswith(".evt")
]
num = len(filenames)


def process_files(filename, i):

    error = False

    # Specify the input file, the prefix for the output file, the attitude file and the terminal output file.
    infile = filename
    prefix = filename.split("u")[0] + "_" + filename.split(".")[1] + "_"
    attfile = filename.split("u", 1)[0] + "pat.fits"
    terminal_output_file = path + "output_uvotimage_" + filename.split(".")[0] + ".txt"

    # Open the file and take the RA, DEC and roll from the header.
    header = fits.open(path + filename)[0].header
    ra = header["RA_PNT"]
    dec = header["DEC_PNT"]
    pa = header["PA_PNT"]

    # Open the terminal output file and run uvotimage with the specified parameters.
    # uvotimage help page: https://heasarc.gsfc.nasa.gov/lheasoft/ftools/headas/uvotimage.html
    with open(terminal_output_file, "w") as terminal:
        try:
            subprocess.run(
                (
                    "uvotimage"
                    f" infile={infile}"
                    f" prefix={prefix}"
                    f" attfile={attfile}"
                    " teldeffile=CALDB alignfile=CALDB"
                    f" ra={ra}"
                    f" dec={dec}"
                    f" roll={pa}"
                    " mod8corr=yes refattopt='ANGLE_d=5,OFFSET_s=1000'"
                ),
                cwd=path,
                shell=True,
                stdout=terminal,
                check=True,
            )
        except subprocess.CalledProcessError:
            error = True

    # todo: do validation outside this function, so print statements present in order
    # Check if the sky image was successfully created.
    with open(terminal_output_file, "r") as file:
        for line in file:
            # If the word "error" is encountered, print an error message.
            if "error" in line:
                print("An error has occured for image " + filename)
                error = True

            # If uvotimage skipped an event based image HDU, let the user know.
            if "skipping event based image HDU" in line:
                print(line, " in file " + filename)

    # Print user information.
    print(f"Sky image created for all (other) frames of {filename} ({i})/{num})")

    return error


with Pool() as p:
    errors = p.starmap(process_files, zip(filenames, range(len(filenames))))


# Print user information.
if not any(errors):
    print("Sky images were successfully created for all raw images and event files.")
