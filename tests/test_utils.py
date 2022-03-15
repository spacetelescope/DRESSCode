import numpy as np

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
