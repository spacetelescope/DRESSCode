#!/usr/bin/env python3

import argparse
from typing import Optional, Sequence


def main(argv: Optional[Sequence[str]] = None) -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument("image_urls", help="image urls, comma separated")
    args = parser.parse_args(argv)

    image_urls = args.image_urls.split(",")

    table_str = "|primary|coincidence loss|\n|:---:|:---:|\n"
    for coincidence_url, primary_url in zip(image_urls[0::2], image_urls[1::2]):
        table_str += f"|{primary_url}|{coincidence_url}|\n"

    print(table_str)

    return 0


if __name__ == "__main__":
    exit(main())
