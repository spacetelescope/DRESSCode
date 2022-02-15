import os

import numpy as np
from scipy.ndimage import convolve


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


def windowed_sum(arr: np.ndarray, radius: int) -> np.ndarray:
    """Sum around a radius of each element in an array
    radius is number of pixels in x/y around each pixel to include
    e.g. radius=1 means the pixel itself and the 8 surrounding pixels
    Implementation: convolution
    """

    kernel = np.ones((radius * 2 + 1, radius * 2 + 1), dtype=int)
    return convolve(arr, kernel, mode="constant", cval=0.0)


def windowed_var(arr: np.ndarray, radius: int) -> np.ndarray:
    """Calculate the variance of a window around each pixel in an array
    Adapted from the this SO: https://stackoverflow.com/a/18423835/532963
    We use our windowed_sum convolution calc. which performs better with nan's
    This is the same algorithm as https://stackoverflow.com/a/18422519/532963
    to computer the variance using just the sum of squares and sum of values in a window
    """
    diameter = radius * 2 + 1
    win_a = windowed_sum(arr, radius)[radius:-radius, radius:-radius]
    win_a2 = windowed_sum(arr * arr, radius)[radius:-radius, radius:-radius]
    return (win_a2 - win_a * win_a / diameter / diameter) / diameter / diameter


def windowed_std(arr: np.ndarray, radius: int) -> np.ndarray:

    output = np.full_like(arr, np.nan, dtype=np.float64)

    var_arr = windowed_var(arr, radius)
    std_arr = np.sqrt(var_arr)
    output[radius:-radius, radius:-radius] = std_arr

    return output
