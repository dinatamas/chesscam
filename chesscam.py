#!/usr/bin/env python3
#
# Command line interface for chesscam.
#
import argparse
import logging
import os
from pathlib import Path
import sys

from chesscam.detect import segment_board

HELP = '''\
Usage: chesscam.py IMG

Perform detection function on the input IMAGE.
Press any button to continue running when an image is shown.

Optional arguments:
  -h, --help    Print this help message and exit.'''


if __name__ == '__main__':
    logging.basicConfig()
    logger = logging.getLogger('chesscam')
    logger.setLevel(logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('img', type=Path)
    parser.print_help = lambda: print(HELP)
    args = parser.parse_args()

    if not os.access(args.img, mode=os.R_OK):
        logger.critical('Input image cannot be opened')
        sys.exit(1)
    if not (squares := segment_board(args.img)):
        logger.critical('Detection failed')
        sys.exit(1)
