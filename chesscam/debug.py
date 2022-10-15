from copy import copy
from random import randint

import cv2 as cv
import numpy as np

from . import cv_utils as cvu


def randcolor():
    return [randint(0, 255) for _ in range(3)]


class Debug:
    imgs = dict()

    def __init__(self, img):
        self.buff = copy(img)

    def board(self, board):
        # Draw lines based on the squares.
        files, ranks = [], []
        for dimension in (files, ranks):
            for i in range(9):
                squares = board[i] if dimension is files else board.T[i]
                if (pts := [p for p in squares if p]):
                    dimension.append(cvu.linear_fit(pts))
        # Extend the lines until the edges of the image.
        h, w = np.shape(self.buff)[:2]
        inf_files = [cvu.fit_line_in_rectangle(f, w, h) for f in files]
        inf_ranks = [cvu.fit_line_in_rectangle(r, w, h) for r in ranks]
        # Collect the points of the board.
        pts = [s for s in board.flatten() if s]
        return self.lines(inf_files + inf_ranks).points(pts)

    def lines(self, lines):
        color = randcolor()
        for a, b in lines:
            cv.line(self.buff, tuple(np.int0(a)), tuple(np.int0(b)), color, 2)
        return self

    def points(self, points):
        color = randcolor()
        for pt in points:
            cv.circle(self.buff, tuple(np.int0(pt)), 5, color, -1)
        return self

    def show(self, name):
        self.imgs[name] = copy(self.buff)
        cv.imshow(name, self.buff)
        cv.waitKey(0)
        cv.destroyAllWindows()
        return self[name]

    def __getitem__(self, name):
        return Debug(self.imgs[name])
