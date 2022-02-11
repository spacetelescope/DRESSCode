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


def sum_window(arr: np.ndarray, radius: int) -> np.ndarray:
    """Sum around a radius of each element in an array
    radius is number of pixels in x/y around each pixel to include
    e.g. radius=1 means the pixel itself and the 8 surrounding pixels
    Implementation: convolution
    """

    kernel = np.ones((radius * 2 + 1, radius * 2 + 1))
    return convolve(arr, kernel, mode="constant", cval=0.0)


# todo: remove this as we're switching to stacked or a diff. implementation
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


def stdev_stacked(arr: np.ndarray, radius: int) -> np.ndarray:
    """
    Standard deviation around a radius by stacking rolled versions of the array
    """

    output = np.full_like(arr, np.nan, dtype=np.float64)

    stacked_arr = arr
    for y in range(-1 * radius, radius + 1):
        for x in range(-1 * radius, radius + 1):
            if x == 0 and y == 0:
                continue
            # roll array in 2d, by x and y
            rolled_arr = np.roll(np.roll(arr, x, axis=1), y, axis=0)

            # set edges of rolled array to np.nan
            if x < 0:
                rolled_arr[:, x:] = np.nan
            elif x > 0:
                rolled_arr[:, 0:x] = np.nan
            if y < 0:
                rolled_arr[y:, :] = np.nan
            elif y > 0:
                rolled_arr[0:y, :] = np.nan

            # stack rolled_arr on top of stacked_arr
            stacked_arr = np.dstack((stacked_arr, rolled_arr))

    # std of stacked array
    # todo: would we rather have nanstd here?
    std_output = np.std(stacked_arr, axis=2)
    # set the edges of the output to np.nan
    output[radius:-radius, radius:-radius] = std_output[radius:-radius, radius:-radius]
    return output
