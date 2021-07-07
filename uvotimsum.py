# uvotimsum.py: Script to co-add frames per type, per filter and per year and to normalize the summed sky images.
# Created on 18-12-2015, updated (to Python 3.6) on 29-10-2018.
# Marjorie Decleir
# Note: This script assumes that all frames have been aspect corrected, and that the files have been separated into different directories based on their observation period (e.g. per year).
# Updated on 05-02-2019 (based on feedback Bob).

# Import the necessary packages.
import os
import shutil
import subprocess

import numpy as np
from astropy.io import fits

import configloader

# Load the configuration file.
config = configloader.load_config()

# Specify the galaxy, the path to the working directory and the different years.
galaxy = config["galaxy"]
path = config["path"] + galaxy + "/working_dir/"
years = config["years"]


# This is the main function.
def main():

    # Loop over the different years.
    for year in years:
        # Print user information.
        print("Year: " + year)
        yearpath = path + year + "/"

        # PART 1: Append all frames per filter and per type.
        # Initialize the counter.
        i = 0

        # Print user information.
        print("Appending all frames...")

        # For all files in the working directory:
        for filename in sorted(os.listdir(yearpath)):

            # Check the type of the image and give the image a type label.
            typelabel = check_type(filename)

            if typelabel == None:
                continue

            # For the mask files: make sure that also the NaN pixels in the exposure maps are included in the mask as well as pixels with a very low exposure time.
            if typelabel == "mk":
                update_mask(yearpath + filename)
                filename = filename.replace(".img", "_new.img")

            # Check the filter of the image and give the image a filter label.
            filterlabel = check_filter(filename)

            # Append all frames to one "total" image.
            i += 1
            append(yearpath + filename, typelabel, filterlabel, i)

        # PART 2: Co-add the frames in each "total" image.
        # Print user information.
        print("Co-adding all frames...")

        if os.path.isfile(yearpath + "all_um2_sk.img"):
            coaddframes(yearpath + "all_um2_sk.img", "grid")
        if os.path.isfile(yearpath + "all_uw2_sk.img"):
            coaddframes(yearpath + "all_uw2_sk.img", "grid")
        if os.path.isfile(yearpath + "all_uw1_sk.img"):
            coaddframes(yearpath + "all_uw1_sk.img", "grid")

        if os.path.isfile(yearpath + "all_um2_ex.img"):
            coaddframes(yearpath + "all_um2_ex.img", "expmap")
        if os.path.isfile(yearpath + "all_uw2_ex.img"):
            coaddframes(yearpath + "all_uw2_ex.img", "expmap")
        if os.path.isfile(yearpath + "all_uw1_ex.img"):
            coaddframes(yearpath + "all_uw1_ex.img", "expmap")

        if os.path.isfile(yearpath + "all_um2_lss.img"):
            coaddframes(yearpath + "all_um2_lss.img", "lssmap")
        if os.path.isfile(yearpath + "all_uw2_lss.img"):
            coaddframes(yearpath + "all_uw2_lss.img", "lssmap")
        if os.path.isfile(yearpath + "all_uw1_lss.img"):
            coaddframes(yearpath + "all_uw1_lss.img", "lssmap")

        # Check the output of the uvotimsum task.
        error = False

        # For all files in the working directory:
        for filename in sorted(os.listdir(yearpath)):

            # If the file is an output text file of uvotimsum, open the file.
            if filename.startswith("output_uvotimsum"):
                file = open(yearpath + filename, "r")
                text = file.read()

                # If the word "error" is encountered, print an error message.
                if (
                    "error" in text
                    or not "created output image" in text
                    or not "all checksums are valid" in text
                ):
                    print(
                        "An error has occured for image all_"
                        + filename.split("_")[2]
                        + "_"
                        + filename.split("_")[3].split(".")[0]
                        + ".img"
                    )
                    error = True

        # PART 3: Normalize the summed sky images.
        # Print user information.
        print("Normalizing the summed sky images...")

        if os.path.isfile(yearpath + "sum_um2_sk.img"):
            norm(yearpath + "sum_um2_sk.img")
        if os.path.isfile(yearpath + "sum_uw2_sk.img"):
            norm(yearpath + "sum_uw2_sk.img")
        if os.path.isfile(yearpath + "sum_uw1_sk.img"):
            norm(yearpath + "sum_uw1_sk.img")

        if error == False:
            print(
                "All frames were successfully co-added and the summed sky images were normalized."
            )


# Functions for PART 1: Appending frames.
# Function to check the type of the image and return a type label.
def check_type(filename):
    if filename.endswith("sk_corr.img"):
        return "sk"
    elif filename.endswith("ex_corr.img"):
        return "ex"
    elif filename.endswith("lss_corr.img"):
        return "lss"
    elif filename.endswith("mk_corr.img"):
        return "mk"


# Function to check the filter of the image and return a filter label.
def check_filter(filename):
    if "um2" in filename:
        return "um2"
    elif "uw2" in filename:
        return "uw2"
    elif "uw1" in filename:
        return "uw1"


# Function to update the mask with pixels that are NaN in the exposure map and pixels that have very low exposure times.
def update_mask(filename):
    # Open the mask file and the exposure map and copy the primary header (extension 0 of hdulist) to a new hdulist.
    hdulist_mk = fits.open(filename)
    hdulist_ex = fits.open(filename.replace("mk", "ex"))
    new_hdu_header = fits.PrimaryHDU(header=hdulist_mk[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    # For all frames in the mask file: Update the mask.
    for i in range(1, len(hdulist_mk)):
        new_mask = hdulist_mk[i].data * (
            np.isfinite(hdulist_ex[i].data) * hdulist_ex[i].data > 1.0
        )
        new_hdu = fits.ImageHDU(new_mask, hdulist_mk[i].header)
        new_hdulist.append(new_hdu)

    # Write the new hdulist to new mask file.
    new_hdulist.writeto(filename.replace(".img", "_new.img"))


# Function to copy the first image of a certain filter and a certain type or to append frames, depending on whether it is the first image or not.
def append(filename, typelabel, filterlabel, i):
    allfile = (
        os.path.dirname(filename) + "/all_" + filterlabel + "_" + typelabel + ".img"
    )

    # If the "total" image of this type and this filter does not yet exist, create it.
    if not os.path.isfile(allfile):
        shutil.copyfile(filename, allfile)
        # Print user information.
        print("File " + os.path.basename(allfile) + " has been created.")
    # Else: append the frames.
    else:
        appendframes(filename, allfile, i)


# Function to open an image and append all its frames to the "total" image.
def appendframes(filename, allfile, i):
    path = os.path.dirname(filename) + "/"

    # Count the total number of images.
    num = sum(
        4 for filename in sorted(os.listdir(path)) if filename.endswith("sk_corr.img")
    )

    hdulist = fits.open(filename)
    for j in range(1, len(hdulist)):
        infile = filename + "+" + str(j)
        totfile = allfile
        subprocess.call("ftappend " + infile + " " + totfile, cwd=path, shell=True)
        # Print user information.
        print(
            "Frame "
            + os.path.basename(infile)
            + " (frame "
            + str(j)
            + "/"
            + str(len(hdulist) - 1)
            + " of image "
            + str(i)
            + "/"
            + str(num)
            + ") appended to "
            + os.path.basename(allfile)
            + "."
        )


# Function for PART 2: Co-add frames.
# Function to co-add all frames of an image.
def coaddframes(allfile, method):
    path = os.path.dirname(allfile) + "/"

    # Specify the output file, the mask file and the terminal output file.
    outfile = allfile.replace("all", "sum")
    maskfile = allfile.rsplit("_", 1)[0] + "_mk.img"
    terminal_output_file = (
        path + "output_uvotimsum" + allfile.split("ll")[1].split(".")[0] + ".txt"
    )

    # Open the terminal output file and run uvotimsum with the specified parameters.
    with open(terminal_output_file, "w") as terminal:
        subprocess.call(
            "uvotimsum infile="
            + allfile
            + " outfile="
            + outfile
            + " method="
            + method
            + " pixsize=0.00027888888381462 exclude=DEFAULT maskfile="
            + maskfile,
            cwd=path,
            shell=True,
            stdout=terminal,
        )
    print(
        "All frames in "
        + os.path.basename(allfile)
        + " have been co-added into "
        + os.path.basename(outfile)
        + "."
    )


# Function for PART 3: Normalizing images.
# Function to normalize an image.
def norm(filename):
    path = os.path.dirname(filename) + "/"

    # Specify the input files and the output file.
    infil1 = filename + "+1"
    infil2 = filename.replace("sk", "ex") + "+1"
    outfil = filename.replace("sk", "nm")

    # Run farith with the specified parameters:
    subprocess.call(
        "farith infil1="
        + infil1
        + " infil2="
        + infil2
        + " outfil="
        + outfil
        + " ops=div null=y",
        cwd=path,
        shell=True,
    )

    # Print user information.
    print(os.path.basename(filename) + " has been normalized.")


if __name__ == "__main__":
    main()
