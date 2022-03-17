from __future__ import annotations

import os
from typing import Optional

import numpy as np
from astropy.convolution import convolve


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


# Function to check the filter of the image and return a filter label.
def check_filter(filename):
    if "_um2_" in filename:
        return "um2"
    elif "_uw2_" in filename:
        return "uw2"
    elif "_uw1_" in filename:
        return "uw1"


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
