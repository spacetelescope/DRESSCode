#!/usr/bin/env python3

"""
corrections.py: Script to apply corrections to the images.
"""

from __future__ import annotations

import os
from argparse import ArgumentParser
from datetime import date, datetime
from typing import Optional, Sequence

import numpy as np
from astropy.io import fits
from astropy.io.fits.hdu.hdulist import HDUList

from dresscode.utils import (
    check_filter,
    load_config,
    windowed_finite_vals,
    windowed_std,
    windowed_sum,
)

ZEROPOINT_PARAMS = {
    "um2": (-2.330e-3, -1.361e-3),
    "uw2": (1.108e-3, -1.960e-3),
    "uw1": (2.041e-3, -1.748e-3),
}


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="path to config.txt", default="config.txt"
    )
    args = parser.parse_args(argv)

    config = load_config(args.config)

    galaxy = config["galaxy"]
    path = config["path"] + galaxy + "/working_dir/"

    file_patt_to_corr = ("sk_corr.img",)
    filenames = [
        filename
        for filename in sorted(os.listdir(path))
        if filename.endswith(file_patt_to_corr)
    ]
    for i, fname in enumerate(filenames):

        fname = path + fname

        # update the masks
        mask_fname = fname.replace("_sk_corr.img", "_mk_corr.img")
        exp_fname = mask_fname.replace("mk", "ex")
        new_mask_fname = mask_fname.replace(".img", "_new.img")
        new_mask_data = update_mask(mask_fname, exp_fname, new_mask_fname)

        # we manipulate the data directly, so open it in memory
        hdul_unmasked = fits.open(fname)

        # apply mask to data, set 0's in mask to nan's
        # coincidence loss correction factor & uncertainties need to take into account missing data
        masked_hdul_fname = fname.replace(".img", "_mk.img")
        hdul_masked = apply_mask(hdul_unmasked, new_mask_data, masked_hdul_fname)

        # apply normalization to data to convert to counts/sec
        norm_hdul_fname = fname.replace(".img", "_nm.img")
        exp_hdul = fits.open(exp_fname)
        hdul_norm = norm(hdul_masked, exp_hdul, norm_hdul_fname)

        # run corrections on data, saving "planes" as separate files

        # Apply a coincidence loss correction.
        print("Applying coincidence loss corrections...")
        coicorr_hdulist, coicorr_filename = coicorr(hdul_norm, fname)

        # Apply a large scale sensitivity correction.
        print("Applying large scale sensitivity corrections...")
        lsscorr_hdulist, lsscorr_filename = lsscorr(coicorr_hdulist, coicorr_filename)

        # Apply a zero point correction.
        # todo: separate file for zero point correction
        print("Applying zero point corrections...")
        zp_corr_hdulist, _ = zeropoint(
            lsscorr_hdulist, lsscorr_filename, *ZEROPOINT_PARAMS[check_filter(fname)]
        )

        # requirement of coadding step, data must be 2D
        print(
            "Splitting the corrected data, coincidence corr, and coicorr_rel into separate files"
        )
        separate_files(zp_corr_hdulist, fname)

        print(f"Corrected image {i + 1}/{len(filenames)}.")

    return 0


def apply_mask(
    hdulist: HDUList, mask: HDUList, output_fname: str, dry_run: bool = False
) -> HDUList:
    """apply the mask to the image frames"""
    new_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for frame, mask_frame in zip(hdulist[1:], mask[1:]):
        new_frame = np.full_like(frame.data, np.nan)
        data_vals = mask_frame.data.astype(bool)
        new_frame[data_vals] = frame.data[data_vals]
        new_hdu = fits.ImageHDU(new_frame, frame.header)
        new_hdulist.append(new_hdu)

    if not dry_run:
        # save the hdulist to a new file
        new_hdulist.writeto(output_fname)

    return new_hdulist


def update_mask(
    mask_fname: str, exp_fname: str, output_fname: str, dry_run: bool = False
) -> HDUList:
    """update the mask with pixels that are NaN in the exposure map and pixels
    that have very low exposure times."""

    # Open the mask file and the exposure map and copy the primary header (extension 0
    # of hdulist) to a new hdulist
    hdulist_mk = fits.open(mask_fname)
    hdulist_ex = fits.open(exp_fname)
    new_hdu_header = fits.PrimaryHDU(header=hdulist_mk[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for mk_frame, ex_frame in zip(hdulist_mk[1:], hdulist_ex[1:]):
        # set mask pixels to 0 that are NaN in the exposure map or whose exposure time is very small
        new_mask = mk_frame.data * np.isfinite(ex_frame.data) * (ex_frame.data > 1.0)
        new_hdu = fits.ImageHDU(new_mask, mk_frame.header)
        new_hdulist.append(new_hdu)

    # Write the new hdulist to new mask file
    if not dry_run:
        new_hdulist.writeto(output_fname)
        print(
            f"{os.path.basename(output_fname)} has been updated with the exposure map"
        )

    return new_hdulist


def norm(
    data_hdul: HDUList, exp_hdul: HDUList, output_fname: str, dry_run: bool = False
) -> HDUList:
    """normalize the data by the exposure map"""
    new_hdu_header = fits.PrimaryHDU(header=data_hdul[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for data_frame, exp_frame in zip(data_hdul[1:], exp_hdul[1:]):
        new_frame = np.full_like(data_frame.data, np.nan)
        finite_vals = np.isfinite(data_frame.data) * np.isfinite(exp_frame.data)
        new_frame[finite_vals] = (
            data_frame.data[finite_vals] / exp_frame.data[finite_vals]
        )
        new_hdu = fits.ImageHDU(new_frame, data_frame.header)
        new_hdulist.append(new_hdu)

    if not dry_run:
        # save the hdulist to a new file
        new_hdulist.writeto(output_fname)
        print(f"{os.path.basename(output_fname)} normalized")

    return new_hdulist


# Functions for PART 1
def coicorr(hdulist, filename):
    """Coincidence loss correction"""
    new_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for frame in hdulist[1:]:
        data = frame.data
        header = frame.header

        # Sum the flux densities (count rates) of the 9x9 surrounding pixels: Craw (counts/s).
        size = 9
        radius = (size - 1) // 2
        window_pixels = windowed_finite_vals(data, radius)
        total_flux = windowed_sum(data, radius)

        # standard deviation of the flux densities in the 9x9 pixels box.
        std = windowed_std(data, radius, win_finite_vals=window_pixels)

        # Obtain the dead time correction factor and the frame time (in s) from the header
        # of the image.
        alpha = header["DEADC"]
        ft = header["FRAMTIME"]

        # Calculate the total number of counts in the 9x9 pixels box: x = Craw*ft (counts).
        # Calculate the minimum and maximum possible number of counts in the 9x9 pixels box.
        total_counts = ft * total_flux
        total_counts_min = ft * (total_flux - window_pixels * std)
        total_counts_max = ft * (total_flux + window_pixels * std)

        # Calculate the polynomial correction factor and the minimum and maximum possible
        # polynomial correction factor.
        f = polynomial(total_counts)
        f_min = polynomial(total_counts_min)
        f_max = polynomial(total_counts_max)

        # If alpha*total_counts_max is larger than 1, replace this value by 0.99. Otherwise,
        # the maximum possible theoretical coincidence-loss-corrected count rate will be NaN
        # in these pixels.
        # todo: ask Marjorie: Could `total_counts_min` also be > 1?
        # todo: they aren't replaced by 0.99, but instead by 0.99 / alpha ... ?
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
        corrfactor_min = (Ctheory_min * f_min) / (total_flux - window_pixels * std)
        corrfactor_max = (Ctheory_max * f_max) / (total_flux + window_pixels * std)

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

        new_hdu = fits.ImageHDU(datacube, header)
        new_hdulist.append(new_hdu)

    new_filename = filename.replace(".img", "_coi.img")
    new_hdulist.writeto(new_filename, overwrite=True)

    print(os.path.basename(filename) + " has been corrected for coincidence loss.")

    return new_hdulist, new_filename


def polynomial(x):
    """Function to calculate the empirical polynomial correction to account for the
    differences between the observed and theoretical coincidence loss correction:

    `f(x) = 1 + a1x + a2x**2 + a3x**3 + a4x**4`
    """
    a1 = 0.0658568
    a2 = -0.0907142
    a3 = 0.0285951
    a4 = 0.0308063
    return 1 + (a1 * x) + (a2 * x**2) + (a3 * x**3) + (a4 * x**4)


# Function for PART 2: Large scale sensitivity correction.
def lsscorr(hdulist, filename):

    new_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    lss_hdulist = fits.open(filename.replace("sk_corr_coi.img", "lss_corr.img"))

    for frame, lss_frame in zip(hdulist[1:], lss_hdulist[1:]):

        data = frame.data[0]
        coicorr = frame.data[1]
        coicorr_rel = frame.data[2]
        header = frame.header

        # Apply the large scale sensitivity correction to the data.
        new_data = data / lss_frame.data
        datacube = [new_data, coicorr, coicorr_rel]

        new_hdu = fits.ImageHDU(datacube, header)
        new_hdulist.append(new_hdu)

    # Write the corrected data to a new image.
    new_filename = filename.replace(".img", "_lss.img")
    new_hdulist.writeto(new_filename, overwrite=True)

    print(
        os.path.basename(filename)
        + " has been corrected for large scale sensitivity variations."
    )

    return new_hdulist, new_filename


# Function for PART 3: Zero point correction.
def zeropoint(hdulist, filename, param1, param2):

    new_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for frame in hdulist[1:]:

        data = frame.data[0]
        coicorr = frame.data[1]
        coicorr_rel = frame.data[2]
        header = frame.header

        obs_date = datetime.fromisoformat(header["DATE-OBS"]).date()
        # Calculate the number of years that have elapsed since the 1st of January 2005.
        first_date = date(2005, 1, 1)
        elapsed_time = obs_date - first_date
        years_passed = elapsed_time.days / 365.25

        # Calculate the zero point correction.
        zerocorr = 1 + param1 * years_passed + param2 * years_passed**2

        # Apply the correction to the data.
        new_data = data / zerocorr

        # Adapt the header.
        header["ZPCORR"] = zerocorr

        # Write the corrected data to a new image.
        datacube = [new_data, coicorr, coicorr_rel]
        new_hdu = fits.ImageHDU(datacube, header)
        new_hdulist.append(new_hdu)

    new_filename = filename.replace(".img", "_zp.img")
    new_hdulist.writeto(new_filename, overwrite=True)

    print(
        os.path.basename(filename)
        + " has been corrected for sensitivity loss of the detector over time."
    )

    return new_hdulist, new_filename


def separate_files(hdulist, filename):
    """Separate data into different files for data, coicorr and coicorr_rel."""
    data_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    data_hdulist = fits.HDUList([data_hdu_header])

    coicorr_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    coicorr_hdulist = fits.HDUList([coicorr_hdu_header])

    coicorr_rel_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    coicorr_rel_data_hdulist = fits.HDUList([coicorr_rel_hdu_header])
    for frame in hdulist[1:]:

        frame_header = frame.header
        frame_header.remove("PLANE1")
        frame_header.remove("PLANE2")

        data_header = frame_header.copy()
        data_header["PLANE0"] = "primary (counts/s)"
        data = frame.data[0]
        data_hdulist.append(fits.ImageHDU(data, data_header))

        coicorr_header = frame_header.copy()
        coicorr_header["PLANE0"] = "coincidence loss correction factor"
        coicorr = frame.data[1]
        coicorr_hdulist.append(fits.ImageHDU(coicorr, coicorr_header))

        coicorr_rel_header = frame_header.copy()
        coicorr_rel_header[
            "PLANE0"
        ] = "relative coincidence loss correction uncertainty (fraction)"
        coicorr_rel = frame.data[2]
        coicorr_rel_data_hdulist.append(fits.ImageHDU(coicorr_rel, coicorr_rel_header))

    data_filename = filename.replace("coi_lss_zp.img", "coi_lss_zp_data.img")
    data_hdulist.writeto(data_filename, overwrite=True)

    coicorr_filename = filename.replace("coi_lss_zp.img", "coi_lss_zp_coicorr.img")
    coicorr_hdulist.writeto(coicorr_filename, overwrite=True)

    coicorr_rel_filename = filename.replace(
        "coi_lss_zp.img", "coi_lss_zp_coicorr_rel.img"
    )
    coicorr_rel_data_hdulist.writeto(coicorr_rel_filename, overwrite=True)


if __name__ == "__main__":
    exit(main())
