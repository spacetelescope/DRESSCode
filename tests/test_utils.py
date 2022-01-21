import numpy as np

from dresscode import utils

np.set_printoptions(precision=2)  # for debugging/printing


def sum_count_rates_window_loop(arr: np.ndarray, radius: int) -> np.ndarray:
    """Sum around a radius of each element in an array

    Old implementation, only for comparison / equivalence testing

    Implementation: iteration"""

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


def std_count_rates_window_loop(arr: np.ndarray, radius: int, ddof=0) -> np.ndarray:
    """Standard deviation around a radius of each elemnt in an array

    pixels around edges are excluded (edge size=radius)

    Old implementation, only for comparison / equivalence testing

    Implementation: iteration"""

    assert len(arr.shape) == 2, "arr should be 2D"

    output = np.full_like(arr, np.nan, dtype=np.float64)
    height, width = arr.shape
    for y in range(radius, height - radius):
        for x in range(radius, width - radius):
            output[y, x] = np.std(
                arr[y - radius : y + radius + 1, x - radius : x + radius + 1], ddof=ddof
            )
    return output


# test data

input_3_3 = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.float64)
sum_3_3_rad_1 = np.array([[12, 21, 16], [27, 45, 33], [24, 39, 28]], dtype=np.float64)
std_3_3_rad_1 = np.full_like(input_3_3, np.nan, dtype=np.float64)
std_3_3_rad_1[1, 1] = np.std(input_3_3)
std_3_3_rad_3 = np.full_like(input_3_3, np.nan, dtype=np.float64)

input_10_10 = np.arange(100).reshape(10, 10)
std_val = np.std(input_10_10[0:7, 0:7])
std_10_10_rad_3 = np.full_like(input_10_10, np.nan, dtype=np.float64)
std_10_10_rad_3[3:7, 3:7] = std_val

input_10_10_diag = np.eye(10, 10, dtype=np.float64)
std_10_10_diag_rad_3 = np.full_like(input_10_10_diag, np.nan, dtype=np.float64)
std_val_4 = np.std([0] * 45 + [1] * 4)
std_val_5 = np.std([0] * 44 + [1] * 5)
std_val_6 = np.std([0] * 43 + [1] * 6)
std_val_7 = np.std([0] * 42 + [1] * 7)
std_10_10_diag_rad_3[range(3, 7), range(3, 7)] = std_val_7
std_10_10_diag_rad_3[range(4, 7), range(3, 6)] = std_val_6
std_10_10_diag_rad_3[range(3, 6), range(4, 7)] = std_val_6
std_10_10_diag_rad_3[range(5, 7), range(3, 5)] = std_val_5
std_10_10_diag_rad_3[range(3, 5), range(5, 7)] = std_val_5
std_10_10_diag_rad_3[6, 3] = std_val_4
std_10_10_diag_rad_3[3, 6] = std_val_4


input_eye_10_10 = np.eye(10, 10, dtype=np.float64)
sum_eye_10_10_rad_1_diag = np.ones(10, dtype=np.float64) * 3
sum_eye_10_10_rad_1_diag[0] = sum_eye_10_10_rad_1_diag[-1] = 2

# SUM COUNT RATES TESTS


def test_sum_count_rates_window_loop_small():
    """Asserts our test output data matches the iteration version"""
    test_output = sum_count_rates_window_loop(input_3_3, 1)
    assert np.array_equal(test_output, sum_3_3_rad_1, equal_nan=True)

    # eye
    test_output = sum_count_rates_window_loop(input_eye_10_10, 1)
    # check diagonal equal
    assert np.array_equal(
        np.diag(test_output), sum_eye_10_10_rad_1_diag, equal_nan=True
    )


def test_sum_count_rates_window():

    test_output = utils.sum_window(input_3_3, 1)
    assert np.array_equal(test_output, sum_3_3_rad_1, equal_nan=True)

    # eye
    test_output = utils.sum_window(input_eye_10_10, 1)
    # check diagonal equal
    assert np.array_equal(
        np.diag(test_output), sum_eye_10_10_rad_1_diag, equal_nan=True
    )


def test_sum_compare_loop_vs_window():
    """Asserts our iteration version matches the convolve version"""

    data = np.random.random((3, 3))
    output_loop = sum_count_rates_window_loop(data, 1)
    output_window = utils.sum_window(data, 1)
    assert np.allclose(output_loop, output_window, equal_nan=True)

    data = np.random.random((45, 100))
    output_loop = sum_count_rates_window_loop(data, 4)
    output_window = utils.sum_window(data, 4)
    assert np.allclose(output_loop, output_window, equal_nan=True)


# STD COUNT RATES TESTS


def test_std_count_rates_window_loop():
    """Asserts our test output data matches the iteration version"""

    test_output = std_count_rates_window_loop(input_3_3, 1)
    assert np.allclose(test_output, std_3_3_rad_1, equal_nan=True)

    test_output = std_count_rates_window_loop(input_3_3, 3)
    assert np.allclose(test_output, std_3_3_rad_3, equal_nan=True)

    test_output = std_count_rates_window_loop(input_10_10, 3)
    assert np.allclose(test_output, std_10_10_rad_3, equal_nan=True)

    test_output = std_count_rates_window_loop(input_10_10_diag, 3)
    assert np.allclose(test_output, std_10_10_diag_rad_3, equal_nan=True)


def test_std_compare_loop_vs_window():
    """Asserts our iteration version matches the uniform_filter version"""
    data = np.random.random((3, 3))
    output_loop = std_count_rates_window_loop(data, 1)
    output_window = utils.stdev_window(data, 1)
    assert np.allclose(output_loop, output_window, equal_nan=True)

    data = np.random.random((99, 100))
    output_loop = std_count_rates_window_loop(data, 4)
    output_window = utils.stdev_window(data, 4)
    assert np.allclose(output_loop, output_window, equal_nan=True)


def test_std_window():
    test_output = utils.stdev_window(input_3_3, 1)
    assert np.allclose(test_output, std_3_3_rad_1, equal_nan=True)

    test_output = utils.stdev_window(input_3_3, 3)
    assert np.allclose(test_output, std_3_3_rad_3, equal_nan=True)

    test_output = utils.stdev_window(input_10_10, 3)
    assert np.allclose(test_output, std_10_10_rad_3, equal_nan=True)

    test_output = utils.stdev_window(input_10_10_diag, 3)
    assert np.allclose(test_output, std_10_10_diag_rad_3, equal_nan=True)
