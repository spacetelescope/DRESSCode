from __future__ import annotations

import os
import subprocess

import numpy as np
import pytest
from astropy.io import fits

from dresscode import utils

np.set_printoptions(precision=2, threshold=10_000)  # for debugging/printing


def windowed_sum_loop(arr: np.ndarray, radius: int) -> np.ndarray:
    """Sum around a radius of each element in an array

    Old implementation, only for comparison / equivalence testing

    Implementation: iteration"""

    output = np.full_like(arr, np.nan, dtype=np.float64)
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            if np.isfinite(arr[y, x]):
                output[y, x] = np.nansum(
                    arr[
                        max(0, y - radius) : min(y + radius + 1, arr.shape[0]),
                        max(0, x - radius) : min(x + radius + 1, arr.shape[1]),
                    ]
                )
    return output


def windowed_std_loop(arr: np.ndarray, radius: int, ddof=0) -> np.ndarray:
    """Standard deviation around a radius of each elemnt in an array

    pixels around edges are excluded (edge size=radius)

    Old implementation, only for comparison / equivalence testing

    Implementation: iteration"""

    assert len(arr.shape) == 2, "arr should be 2D"

    output = np.full_like(arr, np.nan, dtype=np.float64)
    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            if np.isfinite(arr[y, x]):
                output[y, x] = np.nanstd(
                    arr[
                        max(0, y - radius) : min(y + radius + 1, arr.shape[0]),
                        max(0, x - radius) : min(x + radius + 1, arr.shape[1]),
                    ],
                    ddof=ddof,
                )
    return output


def windowed_finite_vals_loop(arr: np.ndarray, radius: int) -> np.ndarray:
    """Number of finite values around a radius of each element in an array

    only for comparison / equivalence testing

    Implementation: iteration"""

    output = np.full_like(arr, np.nan, dtype=np.float64)

    for y in range(arr.shape[0]):
        for x in range(arr.shape[1]):
            output[y, x] = np.sum(
                np.isfinite(
                    arr[
                        max(0, y - radius) : min(y + radius + 1, arr.shape[0]),
                        max(0, x - radius) : min(x + radius + 1, arr.shape[1]),
                    ]
                )
            )
    return output


# test data

input_3_3 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.float64)
sum_3_3_rad_1 = np.array([[12, 21, 16], [27, 45, 33], [24, 39, 28]], dtype=np.float64)

input_10_10 = np.arange(100, dtype=np.float64).reshape(10, 10)

input_10_10_diag = np.eye(10, 10, dtype=np.float64)

input_eye_10_10 = np.eye(10, 10, dtype=np.float64)
sum_eye_10_10_rad_1_diag = np.ones(10, dtype=np.float64) * 3
sum_eye_10_10_rad_1_diag[0] = sum_eye_10_10_rad_1_diag[-1] = 2

# SUM COUNT RATES TESTS


def test_sum_count_rates_window_loop_small():
    """Asserts our test output data matches the iteration version"""
    test_output = windowed_sum_loop(input_3_3, 1)
    assert np.array_equal(test_output, sum_3_3_rad_1, equal_nan=True)

    # eye
    test_output = windowed_sum_loop(input_eye_10_10, 1)
    # check diagonal equal
    assert np.array_equal(
        np.diag(test_output), sum_eye_10_10_rad_1_diag, equal_nan=True
    )


def test_sum_count_rates_window():

    test_output = utils.windowed_sum(input_3_3, 1)
    assert np.array_equal(test_output, sum_3_3_rad_1, equal_nan=True)

    # eye
    test_output = utils.windowed_sum(input_eye_10_10, 1)
    # check diagonal equal
    assert np.array_equal(
        np.diag(test_output), sum_eye_10_10_rad_1_diag, equal_nan=True
    )


def test_sum_nan_data():
    data = input_10_10.copy()
    data[3:4, 3:4] = np.nan
    output_loop = windowed_sum_loop(data, 1)
    output_window = utils.windowed_sum(data, 1)
    assert np.allclose(output_loop, output_window, equal_nan=True)


def test_sum_compare_loop_vs_window():
    """Asserts our iteration version matches the convolve version"""

    data = np.random.random((3, 3))
    output_loop = windowed_sum_loop(data, 1)
    output_window = utils.windowed_sum(data, 1)
    assert np.allclose(output_loop, output_window, equal_nan=True)

    data = np.random.random((45, 100))
    output_loop = windowed_sum_loop(data, 4)
    output_window = utils.windowed_sum(data, 4)
    assert np.allclose(output_loop, output_window, equal_nan=True)

    # setup
    data = np.random.random((45, 50))
    # throw in some nan's
    nan_indices_y = np.random.choice(np.arange(45), size=10, replace=False)
    nan_indices_x = np.random.choice(np.arange(50), size=10, replace=False)
    data[nan_indices_y, nan_indices_x] = np.nan

    output_loop = windowed_sum_loop(data, 4)
    output_stacked = utils.windowed_sum(data, 4)
    assert np.allclose(output_loop, output_stacked, equal_nan=True)


# STD COUNT RATES TESTS


def test_std_window():
    test_output = utils.windowed_std(input_3_3, 1)
    expected_output = windowed_std_loop(input_3_3, 1)
    assert np.allclose(test_output, expected_output, equal_nan=True)

    test_output = utils.windowed_std(input_3_3, 3)
    expected_output = windowed_std_loop(input_3_3, 3)
    assert np.allclose(test_output, expected_output, equal_nan=True)

    test_output = utils.windowed_std(input_10_10, 3)
    expected_output = windowed_std_loop(input_10_10, 3)
    assert np.allclose(test_output, expected_output, equal_nan=True)

    test_output = utils.windowed_std(input_10_10_diag, 3)
    expected_output = windowed_std_loop(input_10_10_diag, 3)
    assert np.allclose(test_output, expected_output, equal_nan=True)


def test_std_compare_loop_vs_window_vs_stacked():
    """Asserts our iteration version matches the uniform_filter version"""
    data = np.random.random((3, 3))
    output_loop = windowed_std_loop(data, 1)
    output_window = utils.windowed_std(data, 1)
    assert np.allclose(output_loop, output_window, equal_nan=True)

    data = np.random.random((99, 100))
    output_loop = windowed_std_loop(data, 4)
    output_window = utils.windowed_std(data, 4)
    assert np.allclose(output_loop, output_window, equal_nan=True)

    # setup
    data = np.random.random((45, 50))
    # throw in some nan's
    nan_indices_y = np.random.choice(np.arange(45), size=10, replace=False)
    nan_indices_x = np.random.choice(np.arange(50), size=10, replace=False)
    data[nan_indices_y, nan_indices_x] = np.nan

    output_loop = windowed_std_loop(data, 4)
    output_stacked = utils.windowed_std(data, 4)
    assert np.allclose(output_loop, output_stacked, equal_nan=True)


def test_std_nan_data():
    data = input_10_10.copy()
    data[3:4, 3:4] = np.nan
    output_loop = windowed_std_loop(data, 1)
    test_output = utils.windowed_std(data, 1)
    assert np.allclose(output_loop, test_output, equal_nan=True)


def test_windowed_finite_vals():
    data = np.random.random((10, 10))
    data[3:4, 3:4] = np.nan
    output_loop = windowed_finite_vals_loop(data, 1)
    test_output = utils.windowed_finite_vals(data, 1)
    assert np.array_equal(output_loop, test_output)


def test_windowed_finite_vals_larger_arr():
    data = np.random.random((45, 50))
    # throw in some nan's
    nan_indices_y = np.random.choice(np.arange(45), size=10, replace=False)
    nan_indices_x = np.random.choice(np.arange(50), size=10, replace=False)
    data[nan_indices_y, nan_indices_x] = np.nan

    output_loop = windowed_finite_vals_loop(data, 1)
    test_output = utils.windowed_finite_vals(data, 1)
    assert np.array_equal(output_loop, test_output)


@pytest.fixture
def updated_mask_fname(mask_fname, exp_fname):
    new_mask_fname = mask_fname.replace(".img", "_new.img")
    utils.update_mask(mask_fname, exp_fname, new_mask_fname)
    return new_mask_fname


@pytest.fixture
def data_masked_fname(data_fname: str, updated_mask_fname: str) -> str:
    hdulist = fits.open(data_fname)
    mask_hdulist = fits.open(updated_mask_fname)
    output_fname = data_fname.replace(".img", "_mk.img")
    utils.apply_mask(hdulist, mask_hdulist, output_fname)
    return output_fname


def test_update_mask(mask_fname, exp_fname):
    new_mask_fname = mask_fname.replace(".img", "_new.img")
    new_mask = utils.update_mask(mask_fname, exp_fname, new_mask_fname, dry_run=True)

    mask_data = new_mask[1].data
    assert mask_data[0, 0] == 0
    assert mask_data[1, 1] == 0
    assert mask_data[2, 2] == 1
    assert mask_data[3, 3] == 0


def test_apply_mask(data_fname, mask_fname):
    data_hdulist = fits.open(data_fname)
    mask_hdulist = fits.open(mask_fname)

    data_hdulist_masked = utils.apply_mask(data_hdulist, mask_hdulist, "", dry_run=True)

    data = data_hdulist_masked[1].data
    assert np.isnan(data[0, 0])
    assert data[1, 1] == data_hdulist[1].data[1, 1]


def norm_farith(fname: str, exp_fname: str):
    """normalize an image by its exposure map

    used only for testing, for comparison with norm function
    """
    path = os.path.dirname(fname) + "/"

    # Specify the input files and the output file.
    infil1 = fname + "+1"
    infil2 = exp_fname + "+1"
    outfil = fname.replace(".img", "_nm.img")

    # Run farith with the specified parameters:
    subprocess.call(
        f"farith infil1={infil1} infil2={infil2} outfil={outfil} ops=div null=y",
        cwd=path,
        shell=True,
    )

    print(f"{os.path.basename(outfil)} normalized")
    return outfil


def test_norm(data_masked_fname: str, exp_fname: str):

    data_hdul = fits.open(data_masked_fname)
    exp_hdul = fits.open(exp_fname)
    outfname = data_masked_fname.replace(".img", "_nm.img")
    hdul_norm = utils.norm(data_hdul, exp_hdul, outfname, dry_run=True)

    data = hdul_norm[1].data
    assert np.isnan(data[0, 0])  # masked
    assert np.isnan(data[1, 1])  # zero exposure, should be masked in the data
    assert data[1, 2] == data_hdul[1].data[1, 2] / 8


@pytest.mark.skipif(
    os.getenv("CI") == "true", reason="skip on CI, where we don't have farith installed"
)
def test_norm_farith(data_masked_fname: str, exp_fname: str):
    # todo: we could run these tests inside our docker image in CI
    data_hdul = fits.open(data_masked_fname)
    exp_hdul = fits.open(exp_fname)
    outfname = data_masked_fname.replace(".img", "_nm.img")
    hdul_norm = utils.norm(data_hdul, exp_hdul, outfname, dry_run=True)
    data = hdul_norm[1].data

    # compare against norm using farith function
    outfname_farith = norm_farith(data_masked_fname, exp_fname)

    data_farith = fits.open(outfname_farith)[0].data
    assert np.array_equal(data, data_farith, equal_nan=True)


def test_denorm(data_masked_fname: str, exp_fname: str):
    data_hdul = fits.open(data_masked_fname)
    exp_hdul = fits.open(exp_fname)
    norm_fname = data_masked_fname.replace(".img", "_nm.img")
    norm_hdul = utils.norm(data_hdul, exp_hdul, norm_fname, dry_run=True)

    denorm_hdul_fname = norm_fname.replace(".img", "_dn.img")
    denorm_hdul = utils.norm(
        norm_hdul, exp_hdul, denorm_hdul_fname, denorm=True, dry_run=True
    )
    data_denorm = denorm_hdul[1].data

    assert np.array_equal(data_denorm, data_hdul[1].data, equal_nan=True)
    assert not np.array_equal(data_denorm, norm_hdul[1].data, equal_nan=True)
