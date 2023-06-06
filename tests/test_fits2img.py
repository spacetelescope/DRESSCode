"""Test of the script that generates images

Not intended to be run in CI since the script is a part of CI
"""


from pathlib import Path

import fits2img
import pytest


@pytest.mark.parametrize("fmt", [None, "png", "jpeg"])
def test_fmt_outputs(fmt, final_fits_path: Path, tmp_path: Path):
    # create args
    args = [str(final_fits_path), "-o", str(tmp_path)]
    if fmt:
        args += ["-f", fmt]
    else:
        # default is png
        fmt = "png"

    res = fits2img.main(args)
    assert res == 0

    # assert we have files in the tmpdir that match format
    assert len(list(tmp_path.glob(f"*.{fmt}"))) == 3 * 2


def test_args_planes(final_fits_path: Path, tmp_path: Path):
    args = [
        str(final_fits_path),
        "-o",
        str(tmp_path),
        "-f",
        "png",
        "--planes",
        "0",
        "1",
        "3",
    ]
    fits2img.main(args)
    # assert we have files in the tmpdir that match format
    assert len(list(tmp_path.glob("*.png"))) == 3 * 3


def test_args_cobine(final_fits_path: Path, tmp_path: Path):
    args = [
        str(final_fits_path),
        "-o",
        str(tmp_path),
        "-f",
        "png",
        "--combine",
        "--planes",
        "0",
        "1",
        "3",
    ]
    fits2img.main(args)
    # assert we have files in the tmpdir that match format
    assert len(list(tmp_path.glob("*.png"))) == 3
