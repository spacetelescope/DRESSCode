#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional, Sequence

from astropy.io import fits
from astropy.visualization import simple_norm
from matplotlib import pyplot as plt

try:
    from rich import print, traceback

    traceback.install()
except ImportError:
    pass

FILE_PATTERN = "*_final*.fits"

IMAGE_TYPES = [
    (0, "primary_(Jy)"),
    (1, "avg_coincidence_loss_corr_factor"),
    (2, "coincidence_loss_corr_uncertainty_(Jy)"),
    (3, "average_zero_point_corr_factor"),
    (4, "Poisson_noise_(Jy)"),
]


class BadArgumentError(ValueError):
    pass


def gen_img(ax: plt.Axes, primary_image, img_type) -> None:

    ax.axis("off")
    ax.imshow(
        primary_image,
        cmap="gray",
        norm=simple_norm(primary_image, "linear", max_percent=97.5),
        aspect="equal",
        origin="lower",
    )
    # plt.colorbar()  # colorbar causes the images to not have the same size
    ax.set_title(f"{img_type}".replace("_", " "), fontsize=10)


def create_images(
    image_path: Path, output_path: Path, img_fmt: str, planes: list[int], combine: bool
) -> None:
    for p in (p for p in image_path.glob(FILE_PATTERN) if not p.name.startswith(".")):
        # iterate over *_final*.fits
        img_fname = p.absolute()

        print("Loading image:", img_fname)

        # load image using astropy
        image_data = fits.getdata(img_fname, ext=0)

        if combine:
            fig = plt.figure(figsize=(5, 10))
            fig.suptitle(p.stem.replace("_", " "), fontsize=10)
            axes = []
            for i in range(len(planes)):
                axes.append(fig.add_subplot(len(planes), 1, i + 1))
            plt.subplots_adjust(top=0.94)

        # primary is the first image
        for i, img_type in [IMAGE_TYPES[i] for i in planes]:

            primary_image = image_data[i, :, :]

            out_fname = f"{p.stem}_{img_type}.{img_fmt}"
            out_path = Path(output_path / out_fname)

            if combine:
                ax = axes[planes.index(i)]
            else:
                fig = plt.figure()
                fig.subtitle(out_path.stem)
                ax = fig.add_subplot(1, 1, 1)

            gen_img(ax, primary_image, img_type)

            if not combine:
                plt.savefig(
                    out_path,
                    bbox_inches="tight",
                    transparent=False,
                    pad_inches=0,
                    dpi=150,
                )
                print(f"Output: {out_path}")

        if combine:
            out_path = Path(f"{output_path}/{p.stem}.{img_fmt}")
            plt.savefig(
                out_path,
                bbox_inches="tight",
                transparent=False,
                pad_inches=0,
                dpi=150,
            )
            print(f"Output: {out_path}")


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "image_path", help=f"path to images with file pattern: {FILE_PATTERN}"
    )
    parser.add_argument("-o", "--output_path", help="output directory", default=".")
    parser.add_argument("-f", "--fmt", help="output format (png/jpg)", default="png")
    parser.add_argument(
        "--planes",
        metavar="N",
        type=int,
        nargs="+",
        help="planes to plot",
        default=[0, 2],
    )
    parser.add_argument(
        "-c", "--combine", default=False, help="combine planes", action="store_true"
    )

    args = parser.parse_args(argv)

    output_path = Path(args.output_path).expanduser()
    if not output_path.is_dir():
        raise BadArgumentError("Output directory is not a valid path")

    image_path = Path(args.image_path).expanduser()
    if not image_path.is_dir():
        raise BadArgumentError("Image directory is not a valid path")

    if max(args.planes) > len(IMAGE_TYPES) or min(args.planes) < 0:
        raise BadArgumentError("Invalid plane number")

    create_images(image_path, output_path, args.fmt, args.planes, args.combine)

    return 0


if __name__ == "__main__":
    exit(main())
