import os

import numpy as np
from scipy.ndimage import convolve
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


def sum_window(arr: np.ndarray, radius: int) -> np.ndarray:
    """Sum around a radius of each element in an array

    radius is number of pixels in x/y around each pixel to include
    e.g. radius=1 means the pixel itself and the 8 surrounding pixels

    Implementation: convolution
    """

    kernel = np.ones((radius * 2 + 1, radius * 2 + 1))
    return convolve(arr, kernel, mode="constant", cval=0.0)


def stdev_window(arr: np.ndarray, radius: int) -> np.ndarray:
    """Standard deviation around a radius of each element in an array

    Edges, equal to radius, are excluded (set to np.nan)

    radius is number of pixels in x/y around each pixel to include
    e.g. radius=1 means the pixel itself and the 8 surrounding pixels

    Implementation: uniform_filter, for details on algorithm see:
    https://stackoverflow.com/a/18422519/532963
    """

    output = np.full_like(arr, np.nan, dtype=np.float64)
    diameter = 2 * radius + 1

    c1 = uniform_filter(arr, diameter, mode="constant", origin=-radius)
    c2 = uniform_filter(arr * arr, diameter, mode="constant", origin=-radius)
    output_window = ((c2 - c1 * c1) ** 0.5)[: -radius * 2, : -radius * 2]

    output[radius:-radius, radius:-radius] = output_window
    return output
