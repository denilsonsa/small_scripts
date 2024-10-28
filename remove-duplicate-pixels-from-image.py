#!/usr/bin/env python

import argparse
import textwrap
from pathlib import Path
from PIL import Image


def remove_duplicates(img):
    next_x = 0
    duplicates = 0
    prev_line = None
    should_print = False

    for x in range(img.width):
        line = img.crop((x, 0, x + 1, 0 + img.height))
        if line == prev_line:
            duplicates += 1
        else:
            img.paste(line, (next_x, 0))
            next_x += 1
            should_print = True

        if x == img.width - 1:
            should_print = True

        if should_print:
            if prev_line is not None:
                print("{0} duplicate columns".format(duplicates))
            should_print = False
            duplicates = 0
        prev_line = line

    next_y = 0
    duplicates = 0
    prev_line = None
    for y in range(img.height):
        line = img.crop((0, y, 0 + img.width, y + 1))
        if line == prev_line:
            duplicates += 1
        else:
            img.paste(line, (0, next_y))
            next_y += 1
            should_print = True

        if y == img.height - 1:
            should_print = True

        if should_print:
            if prev_line is not None:
                print("{0} duplicate rows".format(duplicates))
            should_print = False
            duplicates = 0
        prev_line = line

    return img.crop((0, 0, next_x, next_y))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Removes all duplicate rows and columns from an image.",
        epilog=textwrap.dedent(
            """
            Imagine you have a pixel-art image, but it has been scaled up.
            Now you want to recover the original 1:1 image.
            This tool can help you with that. Since a scaled up image will have
            consecutive rows (and columns) of identical pixels, we can remove
            the duplicates to get a scaled down version.

            Note, however, this tool is not perfect. If the original pixel art
            already had duplicate rows/cols, then those will be removed as well.
            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-f",
        "--format",
        action="store",
        type=str,
        help="Image format for saving the output. If omitted, detect by outputfile extension.",
    )
    parser.add_argument(
        "inputfile",
        action="store",
        type=argparse.FileType("rb"),
        help="Input file (the scaled up image)",
    )
    parser.add_argument(
        "outputfile",
        action="store",
        type=argparse.FileType("wb"),
        help="Output file (after removing duplicate rows/cols)",
    )
    args = parser.parse_args()
    return args


def main():
    args = parse_args()

    with Image.open(args.inputfile) as img:
        remove_duplicates(img).save(args.outputfile, format=args.format)


if __name__ == "__main__":
    main()
