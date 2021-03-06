"""Test of the script that generates images

Not intended to be run in CI since the script is a part of CI
"""


import os
from pathlib import Path
from tempfile import TemporaryDirectory

import fits2img
import pytest

# location of output files from a finished pipeline run
final_image_dir = "~/Documents/SWIFT_data/NGC0628/working_dir"


@pytest.mark.skipif(os.getenv("CI") == "true", reason="Skip on CI")
@pytest.mark.parametrize("fmt", [None, "png", "jpeg"])
def test_fmt_outputs(fmt):
    with TemporaryDirectory() as tmpdir:
        # create args
        args = [final_image_dir, "-o", tmpdir]
        if fmt:
            args += ["-f", fmt]
        else:
            # default is png
            fmt = "png"

        res = fits2img.main(args)
        assert res == 0

        # assert we have files in the tmpdir that match format
        assert len(list(Path(tmpdir).glob(f"*.{fmt}"))) == 6
