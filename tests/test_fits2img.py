"""Test of the script that generates images

Not intended to be run in CI since the script is a part of CI
"""


from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from fits2img import main

# where ben had some output files from the pipeline
final_image_dir = "~/Documents/SWIFT_data/NGC0628/working_dir"


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

        res = main(args)
        assert res == 0

        # assert we have files in the tmpdir that match format
        assert len(list(Path(tmpdir).glob(f"*.{fmt}"))) == 3