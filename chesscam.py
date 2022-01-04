#!/usr/bin/env python3
#
# Command line interface for chesscam.
#
import argparse
import logging
import os
from pathlib import Path
from sys import exit

import chesscam.chess_utils as chu
from chesscam.debug import Debug
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
    #parser.add_argument('video', type=Path)
    parser.print_help = lambda: print(HELP)
    args = parser.parse_args()

    if not os.access(args.img, mode=os.R_OK):
        logger.critical('Input image cannot be opened')
        exit(1)
    if not (squares := segment_board(args.img)):
        logger.critical('Detection failed')
        exit(1)

    board, squares = chu.construct_board(squares)
    Debug(squares[7][0]).show('white?')

    chu.get_square_changes(board)

    exit(0)

    cap = cv.VideoCapture(str(args.video))
    frame_rate = int(cap.get(5))
    while (_, frame := cap.read())[0]:
        if cap.get(1) % frame_rate == 0:
            pass  # Process the frame.
    cap.release()

    # TODO: Go through every frame (every 1 second?)
    # and get the possible moves via the chess library,
    # create (from, to) pairs based on those, and try
    # to detect in which case do both of those changes
    # trigger. In every case specify the exact kind of
    # change (from empty to what color, or other way).
    # Note: en passant has 3 changes, castling 4.
    # TODO: Register thresholds for empty squares,
    # overhanging and full piece squares for all colours
    # and square colors.
    # Note: Consider the edges vs center of the squares!
    # Some pieces may overhang, but maybe contour detection
    # could also help?
    # TODO: Special case: promotion?
