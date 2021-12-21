import numpy as np

from dresscode import utils


def test_sum_count_rates_window():
    expected_output = np.array(
        [[12, 21, 16], [27, 45, 33], [24, 39, 28]], dtype=np.float64
    )

    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    window = (3, 3)
    test_output = utils.sum_count_rates_window(arr, window)
    assert np.array_equal(test_output, expected_output, equal_nan=True)


def test_sum_count_rates_window_eye():
    expected_output_diag = np.ones(10, dtype=np.float64) * 3
    expected_output_diag[0] = expected_output_diag[-1] = 2

    arr = np.eye(10, 10, dtype=np.float64)
    window = (3, 3)
    test_output = utils.sum_count_rates_window(arr, window)
    # check diagonal equal
    assert np.array_equal(np.diag(test_output), expected_output_diag, equal_nan=True)


def test_sum_count_rates_window_loop_small():
    expected_output = np.array(
        [[12, 21, 16], [27, 45, 33], [24, 39, 28]], dtype=np.float64
    )

    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    test_output = utils.sum_count_rates_window_loop(arr, 1)
    assert np.array_equal(test_output, expected_output, equal_nan=True)


def test_sum_count_rates_window_loop_eye():
    expected_output_diag = np.ones(10, dtype=np.float64) * 3
    expected_output_diag[0] = expected_output_diag[-1] = 2

    arr = np.eye(10, 10, dtype=np.float64)
    test_output = utils.sum_count_rates_window_loop(arr, 1)
    # check diagonal equal
    assert np.array_equal(np.diag(test_output), expected_output_diag, equal_nan=True)


def test_std_count_rates_window():
    expected_output = np.array(
        [
            [1.58113883, 1.70782513, 1.58113883],
            [2.5, 2.5819889, 2.5],
            [1.58113883, 1.70782513, 1.58113883],
        ]
    )
    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    window = (3, 3)
    test_output = utils.std_count_rates_window(arr, window)
    assert np.allclose(test_output, expected_output, equal_nan=True)


def test_window_stdev():
    expected_output = np.array(
        [
            [1.58113883, 1.70782513, 1.58113883],
            [2.5, 2.5819889, 2.5],
            [1.58113883, 1.70782513, 1.58113883],
        ]
    )
    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    test_output = utils.window_stdev(arr, 3)
    assert np.allclose(test_output, expected_output, equal_nan=True)


def test_strided_sliding_std_dev():
    expected_output = np.array(
        [
            [1.58113883, 1.70782513, 1.58113883],
            [2.5, 2.5819889, 2.5],
            [1.58113883, 1.70782513, 1.58113883],
        ]
    )
    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    test_output = utils.strided_sliding_std_dev(arr, 1.5)
    assert np.allclose(test_output, expected_output, equal_nan=True)


def test_std_count_rates_window_loop():
    expected_output = np.array(
        [
            [1.58113883, 1.70782513, 1.58113883],
            [2.5, 2.5819889, 2.5],
            [1.58113883, 1.70782513, 1.58113883],
        ]
    )
    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    test_output = utils.std_count_rates_window_loop(arr, 1)
    assert np.allclose(test_output, expected_output, equal_nan=True)


def test_std_generic_filter():
    expected_output = np.array(
        [
            [1.58113883, 1.70782513, 1.58113883],
            [2.5, 2.5819889, 2.5],
            [1.58113883, 1.70782513, 1.58113883],
        ]
    )
    arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    test_output = utils.std_generic_filter(arr, 3)
    assert np.allclose(test_output, expected_output, equal_nan=True)
