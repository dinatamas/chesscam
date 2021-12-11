import logging

import cv2 as cv
import numpy as np

from .debug import Debug
from . import cv_utils as cvu

logger = logging.getLogger('chesscam')
logger.addHandler(logging.NullHandler())


def segment_board(img):
    # Prepare the base image we'll be working with.
    img = cvu.img_resize(cv.imread(str(img)), size=500)
    h, w = np.shape(img)[:2]
    logger.debug(f'Image resized to {w=} x {h=}')
    debug = Debug(img).show('original')

    # Find the inner corners (kernel) of the chessboard's
    # initially empty 8 x 4 central squares, so 7 x 3 points.
    # Corners are returned column-wise, top-to-bottom, right-to-left.
    ret, kernel = cv.findChessboardCorners(img, (7, 3), None)
    if not ret:
        logger.critical('Unable to detect chessboard kernel')
        return None
    kernel = [tuple(c.ravel()) for c in kernel]
    debug['original'].points(kernel).show('kernel')

    # Detect other points on the picture with subpixel accuracy.
    # https://docs.opencv.org/4.x/dc/d0d/tutorial_py_features_harris.html
    # TODO: Perform detecetion only on smaller area for efficiency.
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    harris = cv.dilate(cv.cornerHarris(gray, 2, 3, 0.04), None)
    ret, harris = cv.threshold(harris, 0.01 * harris.max(), 255, 0)
    if not ret:
        logger.critical('Harris corner detection failed')
        return None
    ret, _, _, harris = cv.connectedComponentsWithStats(np.uint8(harris))
    if not ret:
        logger.critical('Subpixel Harris corner detection failed')
        return None
    crit = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.001)
    harris = cv.cornerSubPix(gray, np.float32(harris), (5, 5), (-1, -1), crit)
    debug['kernel'].points(harris).show('harris')

    # Replace the kernel points with the Harris detected closest points.
    for k in kernel:
        k = cvu.closest_among(harris, k)

    # Build up the board and position the kernel within it.
    # The board is stored file-wise: a1, a2, a3, ..., b1, ..., h8.
    # The transpose of board is the row-wise repsentation (board.T).
    # This variable contains the pixels of the corners of squares (9x9).
    board = np.full((9, 9), None)
    # Reverse the kernel to set proper board order.
    kernel = kernel[::-1]
    for i in range(7):
        for j in range(3):
            board[i+1][j+3] = kernel[i+j*7]
    debug['original'].board(board).show('board')

    # Calculate other points of the chessboard.
    # Perspective is taken into account here.
    # Find the closest Harris detected points to the calculated ones.
    for i in range(3, 6):
        pt = cvu.perspective(board.T[i][1:8])
        board[8][i] = cvu.closest_among(harris, pt)
        pt = cvu.perspective(board.T[i][1:8][::-1])
        board[0][i] = cvu.closest_among(harris, pt)
    debug['original'].board(board).show('board')

    # Go through the missing ranks and calculate + detect the points.
    # Harris detection is only used for empty central squares.
    # TODO: Grid heuristic could be used to guess the number of outliers
    # based on the calculated points, which could be served as input
    # to the Huber regressor.
    for j in range(3):
        for k in (3-j-1, 5+j+1):
            # Calculate next rank of points based on perspective.
            for i in range(9):
                boardrange = board[i][3-j:6+j][::(-1 if k == 3-j-1 else 1)]
                board[i][k] = cvu.perspective(boardrange)
            # Fit a line on the newly added points.
            line1 = cvu.linear_fit_robust(board.T[k][0:9])
            line1 = cvu.fit_line_in_rectangle(line1, w, h)
            # Find the harris points closest to fitted lines.
            harris_ok, harris_not = [], []
            for i in range(9):
                pt = cvu.closest_on_line(line1, board[i][k])
                pt2 = cvu.closest_among(harris, pt, 30)
                if j == 0 and pt2 is not None:
                    board[i][k] = pt2
                    harris_ok.append(pt2)
                else:
                    board[i][k] = pt
                    harris_not.append((i, k))
            # Fit new line on adjusted points.
            # Set the non-harris-found points on the newly fitted line.
            if harris_not:
                line1 = cvu.linear_fit_robust(board.T[k][0:9])
                line2 = cvu.fit_line_in_rectangle(line1, w, h)
                for x, y in harris_not:
                    line3 = cvu.linear_fit(board[x][3-j:6+j])
                    line4 = cvu.fit_line_in_rectangle(line3, w, h)
                    board[x][y] = cvu.intersect_lines(line1, line3)
        debug['original'].board(board).show('board')

    # Return the detected squares.
    return True
