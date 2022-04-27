from __future__ import annotations

import os

import numpy as np
from astropy.convolution import convolve
from astropy.io import fits
from astropy.io.fits.hdu.hdulist import HDUList


def listdir_nohidden(path):
    """generator that yields filepaths that aren't hidden (start with a `.`)"""
    for f in os.listdir(path):
        if not f.startswith("."):
            yield f


def load_config(config_file):
    """Function to open and read the configuration file"""
    config = {}
    with open(config_file) as configfile:
        for line in configfile:
            splitline = line.split("=")
            key, value = splitline[0].strip(), splitline[1].strip()
            if key == "years":
                if ", " in value:
                    value = [y.strip() for y in value.split(",")]
                else:
                    value = [value]
            config[key] = value
    return config


def check_filter(filename: str) -> str:
    """Check the filter of the image and return a filter label"""
    if "_um2_" in filename:
        return "um2"
    elif "_uw2_" in filename:
        return "uw2"
    elif "_uw1_" in filename:
        return "uw1"
    raise ValueError(f"Unknown filter for {filename}")


def windowed_sum(arr: np.ndarray, radius: int) -> np.ndarray:
    """Sum around a radius of each element in an array
    radius is number of pixels in x/y around each pixel to include
    e.g. radius=1 means the pixel itself and the 8 surrounding pixels

    Implementation: convolution
    """

    kernel = np.ones((radius * 2 + 1, radius * 2 + 1), dtype=int)
    return convolve(
        arr,
        kernel,
        boundary="fill",
        fill_value=0.0,
        nan_treatment="fill",
        normalize_kernel=False,
        preserve_nan=True,
    )


def windowed_var(
    arr: np.ndarray, radius: int, win_finite_vals: np.ndarray | None = None
) -> np.ndarray:
    """Calculate the variance of a window around each pixel in an array
    Adapted from the this SO: https://stackoverflow.com/a/18423835/532963
    We use our windowed_sum convolution calc. which can handle nan's

    This is the same algorithm as https://stackoverflow.com/a/18422519/532963
    to computer the variance using just the sum of squares and sum of values in a window
    however we need to add a normalization because we aren't using uniform_filter

    Note: this returns smaller in size than the input array (by radius)
    """

    if win_finite_vals is None:
        win_finite_vals = windowed_finite_vals(arr, radius)
    win_sum = windowed_sum(arr, radius)
    win_sum_2 = windowed_sum(arr * arr, radius)
    output = (win_sum_2 - win_sum * win_sum / win_finite_vals) / win_finite_vals
    return output


def windowed_std(
    arr: np.ndarray, radius: int, win_finite_vals: np.ndarray | None = None
) -> np.ndarray:
    """Standard deviation around a radius of each elemnt in an array"""

    var_arr = windowed_var(arr, radius, win_finite_vals)
    std_arr = np.sqrt(var_arr)

    return std_arr


def windowed_finite_vals(arr: np.ndarray, radius: int) -> np.ndarray:
    """Number of finite values around a radius of each element in an array"""

    finite_arr = np.isfinite(arr).astype(int)
    output = windowed_sum(finite_arr, radius)

    return output


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
        new_hdulist.writeto(output_fname, overwrite=True)

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
        new_hdulist.writeto(output_fname, overwrite=True)
        print(f"Updated exposure map in {os.path.basename(output_fname)}")

    hdulist_mk.close()
    hdulist_ex.close()

    return new_hdulist


def norm(
    data_hdul: HDUList,
    exp_hdul: HDUList,
    output_fname: str = "",
    denorm: bool = False,
    dry_run: bool = False,
) -> HDUList:
    """normalize the data by the exposure map"""
    new_hdu_header = fits.PrimaryHDU(header=data_hdul[0].header)
    new_hdulist = fits.HDUList([new_hdu_header])

    for data_frame, exp_frame in zip(data_hdul[1:], exp_hdul[1:]):
        new_frame = np.full_like(data_frame.data, np.nan)
        finite_vals = (
            np.isfinite(data_frame.data)
            & np.isfinite(exp_frame.data)
            & (exp_frame.data > 0)
        )
        if denorm:
            norm_factor = 1.0 / exp_frame.data[finite_vals]
        else:
            norm_factor = exp_frame.data[finite_vals]
        new_frame[finite_vals] = data_frame.data[finite_vals] / norm_factor
        new_hdu = fits.ImageHDU(new_frame, data_frame.header)
        new_hdulist.append(new_hdu)

    if not dry_run:
        # save the hdulist to a new file
        new_hdulist.writeto(output_fname, overwrite=True)
        print(f"{os.path.basename(output_fname)} normalized")

    return new_hdulist
