import tempfile

import numpy as np
import pytest
from astropy.io import fits

from dresscode import corrections


def fits_file_gen(data):
    header = fits.Header({"example data": "example header"})
    hdu = fits.PrimaryHDU(header=header)
    hdul = fits.HDUList([hdu])
    hdul.append(fits.ImageHDU(data, header=header))
    with tempfile.NamedTemporaryFile() as file:
        hdul.writeto(file.name)
        yield file.name


@pytest.fixture
def mask_fname():
    mask_data = np.ones((10, 10), dtype=np.uint8)
    mask_data[0, 0] = 0
    yield from fits_file_gen(mask_data)


@pytest.fixture
def exp_fname():
    data = 8 * np.ones((10, 10), dtype=np.uint8)
    data[1, 1] = 0
    yield from fits_file_gen(data)


@pytest.fixture
def data_fname():
    data = np.random.random((10, 10))
    yield from fits_file_gen(data)


def test_update_mask(mask_fname, exp_fname):
    new_mask = corrections.update_mask(mask_fname, exp_fname, dry_run=True)

    mask_data = new_mask[1].data
    assert mask_data[0, 0] == 0
    assert mask_data[1, 1] == 0
    assert mask_data[2, 2] == 1


def test_apply_mask(data_fname, mask_fname):
    data_hdulist = fits.open(data_fname)
    mask_hdulist = fits.open(mask_fname)

    data_hdulist_masked = corrections.apply_mask(
        data_hdulist, mask_hdulist, "", dry_run=True
    )

    data = data_hdulist_masked[1].data
    assert data[0, 0] == 0
    assert data[1, 1] == data_hdulist[1].data[1, 1]
