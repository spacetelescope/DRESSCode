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
    apply_mask,
    check_filter,
    load_config,
    norm,
    update_mask,
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
        # remove pixels that are NaN in the exposure map and pixels that have very low exposure times
        mask_fname = fname.replace("_sk_corr.img", "_mk_corr.img")
        exp_fname = mask_fname.replace("mk", "ex")
        new_mask_fname = mask_fname.replace(".img", "_new.img")
        new_mask_hdul = update_mask(mask_fname, exp_fname, new_mask_fname)

        # we manipulate the data directly, so open it in memory
        unmasked_hdul = fits.open(fname)

        # apply mask to data, set 0's in mask to nan's
        # coincidence loss correction factor & uncertainties need to take into account missing data
        masked_hdul_fname = fname.replace(".img", "_mk.img")
        masked_hdul = apply_mask(unmasked_hdul, new_mask_hdul, masked_hdul_fname)

        # apply normalization to data to convert to counts/sec
        norm_hdul_fname = fname.replace(".img", "_nm.img")
        exp_hdul = fits.open(exp_fname)
        norm_hdul = norm(masked_hdul, exp_hdul, norm_hdul_fname)

        # Apply a coincidence loss correction, saving "planes" as separate files
        print("Applying coincidence loss corrections...")
        coicorr_hdul, coicorr_fname, corrfactor_hdul, corrfactor_unc_hdul = coicorr(
            norm_hdul, fname
        )

        # Apply a large scale sensitivity correction.
        print("Applying large scale sensitivity corrections...")
        lsscorr_hdul, lsscorr_fname = lsscorr(coicorr_hdul, coicorr_fname)

        # Apply a zero point correction
        print("Applying zero point corrections...")
        zp_corr_fname = lsscorr_fname.replace(".img", "_zp.img")
        zp_corr_hdul = zeropoint(
            lsscorr_hdul, zp_corr_fname, *ZEROPOINT_PARAMS[check_filter(fname)]
        )

        # remove normalization to convert back to counts (needed for uvotimsum)
        print("Removing normalization to convert back to counts...")
        primary_cts_fname = zp_corr_fname.replace(".img", "_dn.img")
        primary_cts_hdul = convert_to_cts(zp_corr_hdul, exp_hdul, primary_cts_fname)

        # calc orig counts for each frame (needed for uvotimsum)
        print("Removing correction factor to get uncorrected orig. counts...")
        orig_cts_fname = primary_cts_fname.replace(".img", "_oc.img")
        rem_corr_factor(primary_cts_hdul, corrfactor_hdul, orig_cts_fname)

        # calc the squared coincidence loss uncertainty in counts
        print("Calculating squared coincidence loss uncertainty in counts...")
        sq_coicorr_unc_fname = fname.replace(".img", "_coicorr_unc_sq_cts.img")
        coicorr_uncert_cts(primary_cts_hdul, corrfactor_unc_hdul, sq_coicorr_unc_fname)

        print("Calculating the zero point correction in counts...")
        zp_corr_cts_fname = fname.replace(".img", "_zp_cts.img")
        zp_corr_cts(primary_cts_hdul, zp_corr_cts_fname)

        print(f"Corrected image {i + 1}/{len(filenames)}.")

        # close all the hdu lists
        unmasked_hdul.close()
        exp_hdul.close()

    return 0


def coicorr(hdulist: HDUList, fname: str):
    """Coincidence loss correction"""
    new_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    coi_loss_corr_hdl = fits.HDUList([new_hdu_header])
    corrfactor_hdl = fits.HDUList([new_hdu_header])
    coicorr_unc_hdl = fits.HDUList([new_hdu_header])

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

        # Get dead time correction factor and frame time (in s)
        alpha = header["DEADC"]
        ft = header["FRAMTIME"]  # normally 11 ms, time between readouts

        # Calculate the total number of counts in the 9x9 pixels box: x = Craw*ft (counts).
        total_counts = ft * total_flux
        # Calculate the minimum and maximum possible number of counts in the 9x9 pixels box.
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
        # todo: handle NaN's
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
        # todo: handle NaN's
        coicorr_rel = coicorr_unc / new_data
        coicorr_rel[coicorr_unc == 0.0] = 0.0

        print(
            "The median coincidence loss correction factor for image "
            + os.path.basename(fname)
            + " is "
            + str(np.nanmedian(corrfactor))
            + " and the median relative uncertainty on the corrected data is "
            + str(np.nanmedian(coicorr_rel))
            + "."
        )

        # todo: should we keep these in the header somewhere?
        # header["PLANE0"] = "primary (counts/s)"
        # header["PLANE1"] = "coincidence loss correction factor"
        # header["PLANE2"] = "relative coincidence loss correction uncertainty (fraction)"

        # Write the corrected data, coincidence loss correction factor, and relative uncertainty
        coi_loss_corr_hdl.append(fits.ImageHDU(new_data, header))
        corrfactor_hdl.append(fits.ImageHDU(corrfactor, header))
        coicorr_unc_hdl.append(fits.ImageHDU(coicorr_rel, header))

    new_fname = fname.replace(".img", "_coi.img")
    coi_loss_corr_hdl.writeto(new_fname, overwrite=True)
    corrfactor_hdl.writeto(new_fname.replace(".img", "_corrfactor.img"), overwrite=True)
    coicorr_unc_hdl.writeto(
        new_fname.replace(".img", "_coicorr_unc.img"), overwrite=True
    )

    print(f"{os.path.basename(fname)} has been corrected for coincidence loss.")

    return coi_loss_corr_hdl, new_fname, corrfactor_hdl, coicorr_unc_hdl


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


def lsscorr(hdulist: HDUList, fname: str):
    """Large scale sensitivity correction"""

    new_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    lss_hdulist = fits.open(fname.replace("sk_corr_coi.img", "lss_corr.img"))

    for frame, lss_frame in zip(hdulist[1:], lss_hdulist[1:]):
        data = frame.data
        header = frame.header

        # Apply the large scale sensitivity correction to the data
        new_data = data / lss_frame.data

        new_hdu = fits.ImageHDU(new_data, header)
        new_hdulist.append(new_hdu)

    # Write the corrected data to a new image.
    new_fname = fname.replace(".img", "_lss.img")
    new_hdulist.writeto(new_fname, overwrite=True)

    print(
        os.path.basename(fname)
        + " has been corrected for large scale sensitivity variations."
    )

    lss_hdulist.close()

    return new_hdulist, new_fname


def zeropoint(hdulist: HDUList, out_fname: str, param1: float, param2: float):
    """Zero point correction (sensitivity loss over time)"""

    new_hdu_header = fits.PrimaryHDU(header=hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for frame in hdulist[1:]:
        data = frame.data
        header = frame.header

        obs_date = datetime.fromisoformat(header["DATE-OBS"]).date()
        # Calculate the number of years that have elapsed since the 1st of January 2005.
        first_date = date(2005, 1, 1)
        elapsed_time = obs_date - first_date
        # todo: update to correctly account for leap years
        years_passed = elapsed_time.days / 365.25

        # Calculate the zero point correction.
        zerocorr = 1 + param1 * years_passed + param2 * years_passed**2

        # Apply the correction to the data.
        new_data = data / zerocorr

        # Adapt the header.
        header["ZPCORR"] = zerocorr

        # Write the corrected data to a new image
        new_hdu = fits.ImageHDU(new_data, header)
        new_hdulist.append(new_hdu)

    new_hdulist.writeto(out_fname, overwrite=True)

    print(
        f"{os.path.basename(out_fname)} has been corrected for sensitivity loss of the detector over time."
    )

    return new_hdulist


def convert_to_cts(data_hdulist: HDUList, exp_hdul: HDUList, out_fname: str):
    """Convert corrected normalized data back to counts"""

    new_hdu_header = fits.PrimaryHDU(header=data_hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    # denorm
    primary_cts_hdul = norm(data_hdulist, exp_hdul, denorm=True, dry_run=True)

    # set any NaNs to zero
    for primary_cts_frame in primary_cts_hdul[1:]:
        primary_cts_data = primary_cts_frame.data
        primary_cts_data[np.isnan(primary_cts_data)] = 0

        new_hdu = fits.ImageHDU(primary_cts_data, primary_cts_frame.header)
        new_hdulist.append(new_hdu)

    # Write the counts data to a new image
    new_hdulist.writeto(out_fname, overwrite=True)

    print(f"{os.path.basename(out_fname)} has been converted to counts for summing.")

    return new_hdulist


def rem_corr_factor(data_hdulist: HDUList, corrfactor_hdul: HDUList, out_fname: str):
    """Remove the correction factor on count data for uvotimsum to yield original counts"""

    # "coincidence loss correction factor" cannot simply be summed
    # What we want is a weighted average of the factors (weighted by counts).
    # To achieve this, we can “undo” the correction for a moment and calculate the counts
    # as if no coincidence correction happened,
    # i.e. orig_counts = primary / corr_factor (where orig_counts is the uncorrected counts).
    # Make sure primary is in counts.
    # We can then sum all the original counts with uvotimsum in the same way as we sum primary.
    # The weighted correction factor for the summed image is then F = summed_primary / summed_orig_counts.

    new_hdu_header = fits.PrimaryHDU(header=data_hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for primary_frame, corr_factor_frame in zip(data_hdulist[1:], corrfactor_hdul[1:]):
        isfinite = (
            np.isfinite(primary_frame.data)
            & np.isfinite(corr_factor_frame.data)
            & (corr_factor_frame.data > 0)
        )
        orig_counts = np.full_like(primary_frame.data, 0)
        orig_counts[isfinite] = (
            primary_frame.data[isfinite] / corr_factor_frame.data[isfinite]
        )
        header = primary_frame.header

        new_hdu = fits.ImageHDU(orig_counts, header)
        new_hdulist.append(new_hdu)

    # Write the original counts data to a new image.
    new_hdulist.writeto(out_fname, overwrite=True)

    return new_hdulist


def coicorr_uncert_cts(
    data_hdulist: HDUList, corrfactor_unc_hdul: HDUList, out_fname: str
):
    """Convert the coincidence loss correction uncertainty in counts, squared"""

    # "coincidence loss correction uncertainty":
    # convert the uncertainty from a relative fraction to an uncertainty in counts
    # multiply the rel_unc frame with the primary frame (in counts).

    new_hdu_header = fits.PrimaryHDU(header=data_hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for primary_frame, corr_factor_rel_unc_frame in zip(
        data_hdulist[1:], corrfactor_unc_hdul[1:]
    ):
        header = primary_frame.header

        coi_loss_corr_unc_cts_squared = np.square(
            primary_frame.data * corr_factor_rel_unc_frame.data
        )
        coi_loss_corr_unc_cts_squared[np.isnan(coi_loss_corr_unc_cts_squared)] = 0

        new_hdu = fits.ImageHDU(coi_loss_corr_unc_cts_squared, header)
        new_hdulist.append(new_hdu)

    # write the squared coincidence loss correction uncertainty to a new image
    new_hdulist.writeto(out_fname, overwrite=True)

    print(
        os.path.basename(out_fname)
        + " squared coincidence loss correction uncertainty counts have been calculated (for summing)."
    )

    return new_hdulist


def zp_corr_cts(data_hdulist: HDUList, out_fname: str):
    """undo the zero point correction for summing / later calculation of weighted factor

    data_hdulist (in counts)
        needs to contain the ZPCORR header
    """

    new_hdu_header = fits.PrimaryHDU(header=data_hdulist[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for primary_frame in data_hdulist[1:]:
        header = primary_frame.header
        zp_corr_cts_data = primary_frame.data * header["ZPCORR"]
        zp_corr_cts_data[np.isnan(zp_corr_cts_data)] = 0
        new_hdu = fits.ImageHDU(zp_corr_cts_data, header)
        new_hdulist.append(new_hdu)

    # Write the zero point correction counts to a new image.
    new_hdulist.writeto(out_fname, overwrite=True)

    print(
        os.path.basename(out_fname)
        + " zero point correction counts have been calculated (for summing)."
    )

    return new_hdulist


if __name__ == "__main__":
    exit(main())
