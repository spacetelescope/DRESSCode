import tempfile

import numpy as np
import pytest
from astropy.io import fits


def fits_file_gen(data, suffix=".img"):
    header = fits.Header({"EX_DATA": "example header"})
    hdu = fits.PrimaryHDU(header=header)
    hdul = fits.HDUList([hdu])
    # create several frames
    for _ in range(3):
        hdul.append(fits.ImageHDU(data, header=header))
    with tempfile.NamedTemporaryFile(suffix=suffix) as file:
        hdul.writeto(file.name)
        yield file.name


@pytest.fixture
def mask_fname():
    mask_data = np.ones((10, 10), dtype=np.uint8)
    mask_data[0, 0] = 0
    yield from fits_file_gen(mask_data, suffix="_mk_corr.img")


@pytest.fixture
def exp_fname():
    data = 8 * np.ones((10, 10), dtype=np.float32)
    data[1, 1] = 0
    data[3, 3] = np.nan
    yield from fits_file_gen(data, "_ex_corr.img")


@pytest.fixture
def data_fname():
    data = np.random.random((10, 10))
    yield from fits_file_gen(data, "_sk_corr.img")
