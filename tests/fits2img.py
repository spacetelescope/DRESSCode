#!/usr/bin/env python3

import argparse
from pathlib import Path
from typing import Optional, Sequence

from astropy.io import fits
from astropy.visualization import simple_norm
from matplotlib import pyplot as plt

FILE_PATTERN = "*_final*.fits"


class BadArgumentError(ValueError):
    pass


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "image_path", help=f"path to images with file pattern: {FILE_PATTERN}"
    )
    parser.add_argument("-o", "--output_path", help="output directory", default=".")
    parser.add_argument("-f", "--fmt", help="output format (png/jpg)", default="png")

    args = parser.parse_args(argv)

    output_path = Path(args.output_path).expanduser()
    if not output_path.is_dir():
        raise BadArgumentError("Output directory is not a path")

    image_path = Path(args.image_path).expanduser()

    for p in image_path.glob(FILE_PATTERN):
        # iterate over final*.fits
        img_fname = p.absolute()

        # load image using astropy
        image_data = fits.getdata(img_fname, ext=0)

        # primary is the first image
        primary_image = image_data[0, :, :]

        plt.figure()
        plt.axis("off")
        plt.imshow(
            primary_image,
            cmap="gray",
            norm=simple_norm(primary_image, "linear", max_percent=97.5),
            aspect="auto",
            origin="lower",
        )
        plt.colorbar()
        plt.savefig(
            f"{output_path}/{p.stem}.{args.fmt}",
            bbox_inches="tight",
            transparent=False,
            pad_inches=0,
            dpi=150,
        )
    return 0


if __name__ == "__main__":
    exit(main())
