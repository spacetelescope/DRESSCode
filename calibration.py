"""
calibration.py: Script to convert the units of the images from counts/s to Jy and to
correct for the aperture calibration.
"""

import os

# Import the necessary packages.
from astropy.io import fits

import configloader

# Load the configuration file.
config = configloader.load_config()

# Specify the galaxy, the path to the working directory and the different years.
galaxy = config["galaxy"]
path = config["path"] + galaxy + "/working_dir/"


# This is the main function.
def main():

    # Print user information.
    print(
        "Converting the units of the final image from counts/s to Jy and correcting "
        "for the aperture calibration..."
    )

    # Specify the conversion factors.
    factor_UVW2 = 8.225e-28 * 1.0e23
    factor_UVM2 = 1.396e-27 * 1.0e23
    factor_UVW1 = 9.524e-28 * 1.0e23

    # Correct for the fact that the conversion factors were determined using 5" radius
    # apertures.
    factor_UVW2 = factor_UVW2 / 1.1279
    factor_UVM2 = factor_UVM2 / 1.1777
    factor_UVW1 = factor_UVW1 / 1.1567

    # Convert the units of the images.
    if os.path.isfile(path + "total_sum_uw2_nm.fits"):
        convert(path + "total_sum_uw2_nm.fits", factor_UVW2)
    if os.path.isfile(path + "total_sum_um2_nm.fits"):
        convert(path + "total_sum_um2_nm.fits", factor_UVM2)
    if os.path.isfile(path + "total_sum_uw1_nm.fits"):
        convert(path + "total_sum_uw1_nm.fits", factor_UVW1)


# Function to convert the units of an image.
def convert(filename, factor):
    # Open the image and convert the units.
    hdulist = fits.open(filename)
    header = hdulist[0].header
    primary = hdulist[0].data[0] * factor
    coicorr_unc = hdulist[0].data[2] * primary
    poisson = hdulist[0].data[4] * primary

    # Adjust the header.
    header["PLANE0"] = "primary (Jy)"
    header["PLANE2"] = "coincidence loss correction uncertainty (Jy)"
    header["PLANE4"] = "Poisson noise (Jy)"

    # Save the converted image.
    new_hdu = fits.PrimaryHDU(
        [primary, hdulist[0].data[1], coicorr_unc, hdulist[0].data[3], poisson], header
    )
    new_hdu.writeto(
        filename.replace("total_sum", galaxy + "_final").replace("nm", "Jy"),
        overwrite=True,
    )


if __name__ == "__main__":
    main()
