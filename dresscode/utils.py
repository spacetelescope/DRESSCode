import os
from typing import Tuple

import numpy as np
from scipy.ndimage import convolve, generic_filter
from scipy.ndimage.filters import uniform_filter


def listdir_nohidden(path):
    """generator that yields filepaths that aren't hidden (start with a `.`)"""
    for f in os.listdir(path):
        if not f.startswith("."):
            yield f


def load_config(config_file):
    """Function to open and read the configuration file"""
    config = {}
    with open(config_file, "r") as configfile:
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


def sum_count_rates_window(arr: np.ndarray, window: Tuple[int, int]) -> np.ndarray:
    """Sum the flux densitities (count rates) of surrounding pixels: Craw (Counts/s)

    window values should be odd

    Implementation: convolution
    """

    kernel = np.ones(window)
    return convolve(arr, kernel, mode="constant", cval=0.0)


def sum_count_rates_window_loop(arr: np.ndarray, radius: int) -> np.ndarray:
    """Sum the flux densitities (count rates) of surrounding pixels: Craw (Counts/s)

    Implementation: slow for loop"""

    output = np.full_like(arr, np.nan, dtype=np.float64)
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            output[y, x] = np.sum(
                arr[
                    max(0, y - radius) : min(y + radius + 1, arr.shape[0]),
                    max(0, x - radius) : min(x + radius + 1, arr.shape[1]),
                ]
            )
    return output


# https://stackoverflow.com/questions/18419871/improving-code-efficiency-standard-deviation-on-sliding-windows
# https://stackoverflow.com/questions/1174984/how-to-efficiently-calculate-a-running-standard-deviation


def std_count_rates_window(arr: np.ndarray, window: Tuple[int, int]) -> np.ndarray:
    """Std of flux densitities of surrounding pixels

    This does not give the correct answer because we need to do the operations within
    the window, not element-wise

    Implementation: convolution"""

    # sqrt( sum ( ( xi - mean(x) ) ** 2 ) / N )

    kernel = np.ones(window)

    # use this to get the correct divisor around edges for mean calcs
    vals = np.ones_like(arr)
    divisor = convolve(vals, kernel, mode="constant", cval=0.0)

    mean_flux = convolve(arr, kernel, mode="constant", cval=0.0) / divisor

    # in a window subtract the mean
    # kernel =

    # difference between each pixel and mean
    flux_sub_mean = arr - mean_flux

    flux_sq_mean = (
        convolve(flux_sub_mean ** 2, kernel, mode="constant", cval=0.0) / divisor
    )
    output = np.sqrt(flux_sq_mean)
    return output


def std_count_rates_window_loop(arr: np.ndarray, radius: int) -> np.ndarray:
    """Std of flux densitities of surrounding pixels

    Implementation: slow for loop"""

    output = np.full_like(arr, np.nan, dtype=np.float64)
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            output[y, x] = np.std(
                arr[
                    max(0, y - radius) : min(y + radius + 1, arr.shape[0]),
                    max(0, x - radius) : min(x + radius + 1, arr.shape[1]),
                ],
                ddof=0,
            )
    return output


def window_stdev(arr, radius):
    """This is not returning valid answers, could be incorrect passing of radius"""
    c1 = uniform_filter(arr, radius * 2, mode="constant", origin=-radius)
    c2 = uniform_filter(arr * arr, radius * 2, mode="constant", origin=-radius)
    return ((c2 - c1 * c1) ** 0.5)[: -radius * 2 + 1, : -radius * 2 + 1]


def strided_sliding_std_dev(data, radius=5):
    """This returns a reduced shaped array. There may be memory consumption issues for
    large arrays."""
    windowed = rolling_window(data, (int(2 * radius), int(2 * radius)))
    shape = windowed.shape
    windowed = windowed.reshape(shape[0], shape[1], -1)
    return windowed.std(axis=-1)


def rolling_window(a, window):
    """Takes a numpy array *a* and a sequence of (or single) *window* lengths
    and returns a view of *a* that represents a moving window."""
    if not hasattr(window, "__iter__"):
        return rolling_window_lastaxis(a, window)
    for i, win in enumerate(window):
        if win > 1:
            a = a.swapaxes(i, -1)
            a = rolling_window_lastaxis(a, win)
            a = a.swapaxes(-2, i)
    return a


def rolling_window_lastaxis(a, window):
    """Directly taken from Erik Rigtorp's post to numpy-discussion.
    <http://www.mail-archive.com/numpy-discussion@scipy.org/msg29450.html>"""
    if window < 1:
        raise ValueError("`window` must be at least 1.")
    if window > a.shape[-1]:
        raise ValueError("`window` is too long.")
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)


def std_generic_filter(arr, size):
    return generic_filter(arr, np.std, size=size)
