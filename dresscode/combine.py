#!/usr/bin/env python3

"""
combine.py: Script to combine the images from different observing periods.

Note: This script assumes that the largest image covers all other images!
"""

import os
from typing import Optional, Sequence

import configloader
import numpy as np
from astropy import wcs
from astropy.io import fits
from ccdproc import CCDData, wcs_project

CONFIG = configloader.load_config()

# Specify the galaxy, the path to the working directory and the different years.
GALAXY = CONFIG["galaxy"]
PATH = CONFIG["path"] + GALAXY + "/working_dir/"
YEARS = CONFIG["years"]
ENLARGE = CONFIG["enlarge"]
ADD_X = int(CONFIG["add_xpix"])
ADD_Y = int(CONFIG["add_ypix"])

FILTERS = ["uw2", "um2", "uw1"]


def main(argv: Optional[Sequence[str]] = None) -> int:

    # PART 1: Convert the units of the corrected images (and their uncertainties) from
    # counts/s to counts.

    print("Converting units from counts/s to counts...")

    # Loop over the different years.
    for year in YEARS:
        yearpath = PATH + year + "/"

        # Loop over the filters.
        for filter in FILTERS:
            # Convert the units of the corrected image.
            if os.path.isfile(yearpath + "sum_" + filter + "_nm_coilsszp.img"):
                convert(yearpath + "sum_" + filter + "_nm_coilsszp.img")

    # PART 2: Reproject the images to one reference image so that they all have the same
    # size.

    print("Reprojecting images...")

    # Loop over the filters.
    for filter in FILTERS:

        # Find out what image is the largest (based on 1 axis only) and take that image
        # as the reference image.
        size = 0
        ref_path = None
        for year in YEARS:
            yearpath = PATH + year + "/"
            if os.path.isfile(yearpath + "sum_" + filter + "_nm_coilsszp_c.img"):
                hdulist = fits.open(yearpath + "sum_" + filter + "_nm_coilsszp_c.img")
                if size < hdulist[0].header["NAXIS1"]:
                    size = hdulist[0].header["NAXIS1"]
                    ref_path = yearpath

        if ref_path is None:
            print(
                "No images were found for filter "
                + filter
                + ". Please verify whether this is correct."
            )
            continue
        else:
            print(
                "Image sum_"
                + filter
                + "_nm_coilsszp_c.img of year "
                + ref_path.split("/")[-2]
                + " will be used as reference image. "
                "Please verify whether this image is large enough to cover all other "
                "images."
            )

        # Open the reference image.
        ref_image = fits.open(ref_path + "sum_" + filter + "_nm_coilsszp_c.img")
        ref_header = ref_image[0].header

        # ------------------------------------------------------------------------------
        # In the case that the reference image is not large enough to cover all other
        # images, embed the reference image into a larger image by adding NaN values
        # around the image.
        if ENLARGE == "yes":
            ref_header = embed(ref_header, ADD_X, ADD_Y)
        # ------------------------------------------------------------------------------

        # Create empty lists for the reprojected images.
        repro_skylist = []
        repro_explist = []

        # Loop over the years.
        for year in YEARS:
            yearpath = PATH + year + "/"

            # Reproject the image (if it is present) to the reference image.
            if os.path.isfile(yearpath + "sum_" + filter + "_nm_coilsszp_c.img"):
                reproject(
                    yearpath + "sum_" + filter + "_nm_coilsszp_c.img",
                    ref_header,
                    repro_skylist,
                    repro_explist,
                )

        # PART 3: Replace all NaNs in the sky images (and uncertainties), and the
        # corresponding pixels in the exposure maps by 0s.
        # Create lists with zeros for the images without NaNs.
        new_skylist = np.zeros_like(repro_skylist)
        new_explist = np.zeros_like(repro_explist)

        # Replace the NaNs.
        for i in range(len(repro_skylist)):
            new_skylist[i], new_explist[i] = replaceNaN(
                repro_skylist[i], repro_explist[i]
            )

        # PART 4: Sum the images of the different years and calculate the Poisson noise.

        print("Summing the images of filter " + filter + "...")

        # Sum the sky images (and uncertainties) and the exposure maps.
        sum_datacube, sum_exp_data, header = sum_years(
            new_skylist, new_explist, filter, ref_path
        )

        # PART 5: Normalize the total sky image.

        print("Normalizing the total sky image of filter " + filter + "...")
        # Normalize the total sky image.
        norm(sum_datacube, sum_exp_data, filter, header)

    return 0


# Function for PART 1: Unit conversion.
# Function to convert the units of an image from count rates to counts.
def convert(filename):
    # Open the image and the corresponding exposure map.
    hdulist = fits.open(filename)
    data = hdulist[0].data[0]
    header = hdulist[0].header

    exp_hdulist = fits.open(filename.replace("nm_coilsszp", "ex"))
    exp_data = exp_hdulist[1].data

    # Convert the units from counts/s to counts.
    new_data = data * exp_data

    # Calculate the coincidence loss correction uncertainty (in counts).
    coicorr_unc = hdulist[0].data[2] * new_data

    # Create a frame with the zero point correction factor.
    f_zp = np.full_like(data, header["ZPCORR"])

    # Adapt the header. Write the converted data and uncertainties to a new image.
    header["PLANE0"] = "primary (counts)"
    header["PLANE2"] = "coincidence loss correction uncertainty (counts)"
    header["PLANE3"] = "zero point correction factor"
    del header["ZPCORR"]
    datacube = [new_data, hdulist[0].data[1], coicorr_unc, f_zp]
    new_hdu = fits.PrimaryHDU(datacube, header)
    new_hdu.writeto(filename.replace(".img", "_c.img"), overwrite=True)


# Functions for PART 2: Reprojection.
# Function to embed an image into a larger image (by updating the header only).
def embed(header, addx, addy):

    # Update the header information.
    header["NAXIS1"] = header["NAXIS1"] + addx * 2
    header["NAXIS2"] = header["NAXIS2"] + addy * 2
    header["CRPIX1"] = header["CRPIX1"] + addx
    header["CRPIX2"] = header["CRPIX2"] + addy

    return header


# Function to reproject an image to a reference image.
def reproject(filename, ref_header, skylist, explist):
    # Open the image.
    hdulist = fits.open(filename)
    datacube = hdulist[0].data
    header = hdulist[0].header

    # Create a list with zeros for the reprojected datacube.
    repro_datacube = [0] * len(datacube)

    # Loop over the different frames in the datacube.
    for i, data in enumerate(datacube):
        # Create a CCDData class object.
        data_ccd = CCDData(
            data, header=header, unit="count", wcs=wcs.WCS(header).celestial
        )
        # Reproject the data to the reference data.
        repro_datacube[i] = np.asarray(
            wcs_project(
                data_ccd,
                wcs.WCS(ref_header).celestial,
                target_shape=(ref_header["NAXIS2"], ref_header["NAXIS1"]),
            )
        )

    # Temporary workaround to update the header of the image.
    new_data = wcs_project(
        data_ccd,
        wcs.WCS(ref_header).celestial,
        target_shape=(ref_header["NAXIS2"], ref_header["NAXIS1"]),
    )
    new_data.write(filename.replace(".img", "_r.img"), format="fits", overwrite=True)
    temp_hdu = fits.open(filename.replace(".img", "_r.img"))
    new_header = temp_hdu[0].header

    # Append the reprojected datacube to the list and write it to a new image.
    skylist.append(np.array(repro_datacube))
    new_hdu = fits.PrimaryHDU(repro_datacube, new_header)
    new_hdu.writeto(filename.replace(".img", "_r.img"), overwrite=True)

    # Reproject the exposure map.
    data_exp_ccd = CCDData.read(
        filename.replace("nm_coilsszp_c", "ex"), unit="count", hdu=1
    )
    repro_data_exp = wcs_project(
        data_exp_ccd,
        wcs.WCS(ref_header).celestial,
        target_shape=(ref_header["NAXIS2"], ref_header["NAXIS1"]),
    )

    # Append the reprojected data to a list and write it to a new image.
    explist.append(np.array(repro_data_exp))
    repro_data_exp.write(
        filename.replace("nm_coilsszp_c", "ex_r"), format="fits", overwrite=True
    )


# Function for PART 3: Replacing NaNs by 0s.
# Function to replace the NaNs in the sky image (and uncertainties), and the
# corresponding pixels in the exposure map by 0s.
def replaceNaN(datacube, expdata):
    # Create a mask for the NaNs in the primary frame of the datacube.
    mask = np.isnan(datacube[0])
    # Replace the masked pixels by 0s in all frames of the datacube.
    for data in datacube:
        data[mask] = 0.0
    # Replace the masked pixels by 0s in the exposure map.
    expdata[mask] = 0.0
    return datacube, expdata


# Function for PART 4: Sum the years and calculate the Poisson noise.
# Function to sum the images (and uncertainties) and exposure maps and to calculate the
# Poisson noise.
def sum_years(skylist, explist, filter, ref_path):
    # Sum the sky frames.
    sum_datacube = np.zeros_like(skylist[0])
    for datacube in skylist:
        sum_datacube = sum_datacube + datacube

    # Calculate the relative coincidence loss correction uncertainty.
    primary = sum_datacube[0]
    coicorr_rel = sum_datacube[2] / primary

    # Calculate a weighted-average coincidence loss correction factor.
    denom = np.zeros_like(skylist[0][0])
    for datacube in skylist:
        notnan = np.isfinite(datacube[0] / datacube[1])
        denom[notnan] += (datacube[0] / datacube[1])[notnan]
    f_coi = primary / denom

    # Calculate a weighted-average zero point correction factor.
    denom = np.zeros_like(skylist[0][0])
    for datacube in skylist:
        notnan = np.isfinite(datacube[0] / datacube[3])
        denom[notnan] += (datacube[0] / datacube[3])[notnan]
    f_zp = primary / denom

    # Calculate the relative Poisson noise.
    poisson_rel = 1.0 / np.sqrt(primary)

    # Obtain the header of the reference image and adjust it.
    header = fits.open(ref_path + "sum_" + filter + "_nm_coilsszp_c_r.img")[0].header
    for i in range(len(skylist[0])):
        del header["PLANE" + str(i)]
    header["PLANE0"] = "primary (counts)"
    header["PLANE1"] = "average coincidence loss correction factor"
    header["PLANE2"] = "relative coincidence loss correction uncertainty (fraction)"
    header["PLANE3"] = "average zero point correction factor"
    header["PLANE4"] = "relative Poisson noise (fraction)"

    # Write the new datacube to a new image.
    new_datacube = np.array([primary, f_coi, coicorr_rel, f_zp, poisson_rel])
    sum_hdu = fits.PrimaryHDU(new_datacube, header)
    sum_hdu.writeto(PATH + "total_sum_" + filter + "_sk.fits", overwrite=True)

    # Sum the exposure maps.
    sum_exp_data = np.zeros_like(explist[0])
    for data in explist:
        sum_exp_data = sum_exp_data + data

    # Write the summed exposure map to a new image.
    exp_header = fits.open(ref_path + "sum_" + filter + "_ex_r.img")[0].header
    sum_exp_hdu = fits.PrimaryHDU(sum_exp_data, exp_header)
    sum_exp_hdu.writeto(PATH + "total_sum_" + filter + "_ex.fits", overwrite=True)
    return new_datacube, sum_exp_data, header


# Function for PART 5: Normalizing the total sky image.
# Function to normalize an image.
def norm(datacube, exp_data, filter, header):
    # Normalize the image
    datacube[0] = datacube[0] / exp_data

    # Adjust the header.
    header["PLANE0"] = "primary (counts/s)"

    # Save the normalized image.
    norm_hdu = fits.PrimaryHDU(datacube, header)
    norm_hdu.writeto(PATH + "total_sum_" + filter + "_nm.fits", overwrite=True)


if __name__ == "__main__":
    exit(main())
