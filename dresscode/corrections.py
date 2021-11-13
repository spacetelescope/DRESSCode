#!/usr/bin/env python3

"""
corrections.py: Script to apply corrections to the images.
"""

import os
from argparse import ArgumentParser
from datetime import date, datetime
from typing import Optional, Sequence

import numpy as np
from astropy.io import fits

from dresscode.utils import load_config


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="path to config.txt", default="config.txt"
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)

    galaxy = config["galaxy"]
    path = config["path"] + galaxy + "/working_dir/"
    years = config["years"]

    # Loop over the different years.
    for year in years:

        print("Year: " + year)
        yearpath = path + year + "/"

        # PART 1: Apply a coincidence loss correction.

        print("Applying coincidence loss corrections...")
        if os.path.isfile(yearpath + "sum_um2_nm.img"):
            coicorr(yearpath + "sum_um2_nm.img")
        if os.path.isfile(yearpath + "sum_uw2_nm.img"):
            coicorr(yearpath + "sum_uw2_nm.img")
        if os.path.isfile(yearpath + "sum_uw1_nm.img"):
            coicorr(yearpath + "sum_uw1_nm.img")

        # PART 2: Apply a large scale sensitivity correction.

        print("Applying large scale sensitivity corrections...")
        if os.path.isfile(yearpath + "sum_um2_nm_coi.img"):
            lsscorr(yearpath + "sum_um2_nm_coi.img")
        if os.path.isfile(yearpath + "sum_uw2_nm_coi.img"):
            lsscorr(yearpath + "sum_uw2_nm_coi.img")
        if os.path.isfile(yearpath + "sum_uw1_nm_coi.img"):
            lsscorr(yearpath + "sum_uw1_nm_coi.img")

        # PART 3: Apply a zero point correction.

        print("Applying zero point corrections...")
        if os.path.isfile(yearpath + "sum_um2_nm_coilss.img"):
            zeropoint(yearpath + "sum_um2_nm_coilss.img", -2.330e-3, -1.361e-3)
        if os.path.isfile(yearpath + "sum_uw2_nm_coilss.img"):
            zeropoint(yearpath + "sum_uw2_nm_coilss.img", 1.108e-3, -1.960e-3)
        if os.path.isfile(yearpath + "sum_uw1_nm_coilss.img"):
            zeropoint(yearpath + "sum_uw1_nm_coilss.img", 2.041e-3, -1.748e-3)

    return 0


# Functions for PART 1: Coincidence loss correction.
def coicorr(filename):
    # Open the image. Create arrays with zeros with the shape of the image.
    hdulist = fits.open(filename)
    data = hdulist[0].data
    header = hdulist[0].header
    total_flux = np.full_like(data, np.nan, dtype=np.float64)
    std = np.full_like(data, np.nan, dtype=np.float64)

    # Loop over all pixels and for each pixel: sum the flux densities (count rates) of
    # the 9x9 surrounding pixels: Craw (counts/s). Calculate the standard deviation in
    # the 9x9 pixels box.
    for x in range(5, data.shape[1] - 5):
        for y in range(5, data.shape[0] - 5):
            total_flux[y, x] = np.sum(data[y - 4 : y + 5, x - 4 : x + 5])
            std[y, x] = np.std(data[y - 4 : y + 5, x - 4 : x + 5])

    # Obtain the dead time correction factor and the frame time (in s) from the header
    # of the image.
    alpha = header["DEADC"]
    ft = header["FRAMTIME"]

    # Calculate the total number of counts in the 9x9 pixels box: x = Craw*ft (counts).
    # Calculate the minimum and maximum possible number of counts in the 9x9 pixels box.
    total_counts = ft * total_flux
    total_counts_min = ft * (total_flux - 81 * std)
    total_counts_max = ft * (total_flux + 81 * std)

    # Calculate the polynomial correction factor and the minimum and maximum possible
    # polynomial correction factor.
    f = polynomial(total_counts)
    f_min = polynomial(total_counts_min)
    f_max = polynomial(total_counts_max)

    # If alpha*total_counts_max is larger than 1, replace this value by 0.99. Otherwise,
    # the maximum possible theoretical coincidence-loss-corrected count rate will be NaN
    # in these pixels.
    if np.sum(alpha * total_counts_max >= 1.0) != 0:
        print(
            "Warning: The following pixels have very high fluxes. The uncertainty on "
            "the correction factor for these pixels is not to be trusted!",
            np.where(alpha * total_counts_max >= 1.0),
        )
    total_counts_max[alpha * total_counts_max >= 1.0] = 0.99 / alpha

    # Calculate the theoretical coincidence-loss-corrected count rate:
    # Ctheory = -ln(1 - alpha*Craw*ft) / (alpha*ft) (counts/s).
    # Calculate the minimum and maximum possible theoretical coincidence-loss-corrected
    # count rate.
    Ctheory = -np.log1p(-alpha * total_counts) / (alpha * ft)
    Ctheory_min = -np.log1p(-alpha * total_counts_min) / (alpha * ft)
    Ctheory_max = -np.log1p(-alpha * total_counts_max) / (alpha * ft)

    # Calculate the coincidence loss correction factor:
    # Ccorrfactor = Ctheory*f(x)/Craw.
    # Calculate the minimum and maximum possible coincidence loss correction factor.
    corrfactor = (Ctheory * f) / total_flux
    corrfactor_min = (Ctheory_min * f_min) / (total_flux - 81 * std)
    corrfactor_max = (Ctheory_max * f_max) / (total_flux + 81 * std)

    # Apply the coincidence loss correction to the data. Apply the minimum and maximum
    # coincidence loss correction to the data.
    new_data = corrfactor * data
    new_data_min = corrfactor_min * data
    new_data_max = corrfactor_max * data

    # Calculate the uncertainty and the relative uncertainty on the coincidence loss
    # correction. Put the relative uncertainty to 0 if the uncertainty is 0 (because in
    # those pixels the flux is also 0 and the relative uncertainty would be NaN).
    coicorr_unc = np.maximum(
        np.abs(new_data - new_data_min), np.abs(new_data_max - new_data)
    )
    coicorr_rel = coicorr_unc / new_data
    coicorr_rel[coicorr_unc == 0.0] = 0.0

    print(
        "The median coincidence loss correction factor for image "
        + os.path.basename(filename)
        + " is "
        + str(np.nanmedian(corrfactor))
        + " and the median relative uncertainty on the corrected data is "
        + str(np.nanmedian(coicorr_rel))
        + "."
    )

    # Adapt the header. Write the corrected data, the applied coincidence loss
    # correction and the relative uncertainty to a new image.
    header["PLANE0"] = "primary (counts/s)"
    header["PLANE1"] = "coincidence loss correction factor"
    header["PLANE2"] = "relative coincidence loss correction uncertainty (fraction)"
    datacube = [new_data, corrfactor, coicorr_rel]
    new_hdu = fits.PrimaryHDU(datacube, header)
    new_hdu.writeto(filename.replace(".img", "_coi.img"), overwrite=True)

    print(os.path.basename(filename) + " has been corrected for coincidence loss.")


# Function to calculate the empirical polynomial correction to account for the
# differences between the observed and theoretical coincidence loss correction:
# f(x) = 1 + a1x + a2x**2 + a3x**3 + a4x**4.
def polynomial(x):
    a1 = 0.0658568
    a2 = -0.0907142
    a3 = 0.0285951
    a4 = 0.0308063
    return 1 + (a1 * x) + (a2 * x ** 2) + (a3 * x ** 3) + (a4 * x ** 4)


# Function for PART 2: Large scale sensitivity correction.
def lsscorr(filename):
    # Open the image and the large scale sensitivity map.
    hdulist = fits.open(filename)
    data = hdulist[0].data[0]
    coicorr = hdulist[0].data[1]
    coicorr_rel = hdulist[0].data[2]
    header = hdulist[0].header

    lss_hdulist = fits.open(filename.replace("nm_coi", "lss"))
    lss_data = lss_hdulist[1].data

    # Apply the large scale sensitivity correction to the data.
    new_data = data / lss_data
    new_datacube = [new_data, coicorr, coicorr_rel]

    # Write the corrected data to a new image.
    new_hdu = fits.PrimaryHDU(new_datacube, header)
    new_hdu.writeto(filename.replace(".img", "lss.img"), overwrite=True)

    print(
        os.path.basename(filename)
        + " has been corrected for large scale sensitivity variations."
    )


# Function for PART 3: Zero point correction.
def zeropoint(filename, param1, param2):
    # Open the file.
    hdulist = fits.open(filename)
    data = hdulist[0].data[0]
    coicorr = hdulist[0].data[1]
    coicorr_rel = hdulist[0].data[2]
    header = hdulist[0].header
    # Calculate the average date of observation.
    start_date = datetime.strptime(header["DATE-OBS"].split("T")[0], "%Y-%m-%d").date()
    end_date = datetime.strptime(header["DATE-END"].split("T")[0], "%Y-%m-%d").date()
    obs_date = (end_date - start_date) / 2 + start_date
    # Calculate the number of years that have elapsed since the 1st of January 2005.
    first_date = date(2005, 1, 1)
    elapsed_time = obs_date - first_date
    years_passed = elapsed_time.days / 365.25

    # Calculate the zero point correction.
    zerocorr = 1 + param1 * years_passed + param2 * years_passed ** 2

    # Apply the correction to the data.
    new_data = data / zerocorr

    # Adapt the header. Write the corrected data to a new image.
    header["ZPCORR"] = zerocorr
    datacube = [new_data, coicorr, coicorr_rel]
    new_hdu = fits.PrimaryHDU(datacube, header)
    new_hdu.writeto(filename.replace(".img", "zp.img"), overwrite=True)

    print(
        os.path.basename(filename)
        + " has been corrected for sensitivity loss of the detector over time."
    )


if __name__ == "__main__":
    exit(main())
