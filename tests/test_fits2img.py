"""Test of the script that generates images

Not intended to be run in CI since the script is a part of CI
"""


import os
from pathlib import Path

import fits2img
import pytest

# location of output files from a finished pipeline run
final_image_dir = "~/Documents/SWIFT_data/NGC0628/working_dir"


@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip on CI")
@pytest.mark.parametrize("fmt", [None, "png", "jpeg"])
def test_fmt_outputs(fmt, tmp_path: Path):
    # create args
    args = [final_image_dir, "-o", str(tmp_path)]
    if fmt:
        args += ["-f", fmt]
    else:
        # default is png
        fmt = "png"

    res = fits2img.main(args)
    assert res == 0

    # assert we have files in the tmpdir that match format
    assert len(list(tmp_path.glob(f"*.{fmt}"))) == 3 * 2


def test_args_planes(tmp_path: Path):

    args = [
        final_image_dir,
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
    assert len(list(tmp_path.glob(f"*.png"))) == 3 * 3


def test_args_cobine(tmp_path: Path):

    args = [
        final_image_dir,
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
    assert len(list(tmp_path.glob(f"*.png"))) == 3
