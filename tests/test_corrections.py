import os
import subprocess
import tempfile

import numpy as np
import pytest
from astropy.io import fits

from dresscode import corrections

np.set_printoptions(precision=2, threshold=10_000)  # for debugging/printing


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
    data = 8 * np.ones((10, 10), dtype=np.uint8)
    data[1, 1] = 0
    yield from fits_file_gen(data, "_ex_corr.img")


@pytest.fixture
def updated_mask_fname(mask_fname, exp_fname):
    new_mask_fname = mask_fname.replace(".img", "_new.img")
    corrections.update_mask(mask_fname, exp_fname, new_mask_fname)
    return new_mask_fname


@pytest.fixture
def data_fname():
    data = np.random.random((10, 10))
    yield from fits_file_gen(data, "_sk_corr.img")


@pytest.fixture
def data_masked_fname(data_fname: str, updated_mask_fname: str) -> str:
    hdulist = fits.open(data_fname)
    mask_hdulist = fits.open(updated_mask_fname)
    output_fname = data_fname.replace(".img", "_mk.img")
    corrections.apply_mask(hdulist, mask_hdulist, output_fname)
    return output_fname


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


def test_update_mask(mask_fname, exp_fname):
    new_mask_fname = mask_fname.replace(".img", "_new.img")
    new_mask = corrections.update_mask(
        mask_fname, exp_fname, new_mask_fname, dry_run=True
    )

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
    assert np.isnan(data[0, 0])
    assert data[1, 1] == data_hdulist[1].data[1, 1]


def test_norm(data_masked_fname: str, exp_fname: str):

    data_hdul = fits.open(data_masked_fname)
    exp_hdul = fits.open(exp_fname)
    outfname = data_masked_fname.replace(".img", "_nm.img")
    hdul_norm = corrections.norm(data_hdul, exp_hdul, outfname, dry_run=True)

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
    hdul_norm = corrections.norm(data_hdul, exp_hdul, outfname, dry_run=True)
    data = hdul_norm[1].data

    # compare against norm using farith function
    outfname_farith = norm_farith(data_masked_fname, exp_fname)

    data_farith = fits.open(outfname_farith)[0].data
    assert np.array_equal(data, data_farith, equal_nan=True)
