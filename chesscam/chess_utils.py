#
# Utilities related to chess.
#
from dataclasses import dataclass
from typing import Literal

import chess
import numpy as np


@dataclass
class SquareChange:
    pos: tuple[int, int]
    promotion: bool
    square_color: Literal['white', 'black']
    from_color: Literal['white', 'black', 'empty']
    to_color: Literal['white', 'black', 'empty']


def construct_board(squares):
    """
    Return the python-chess board based on the square images.
    Technically just orients the starting position.
    """
    if np.average(squares[7][0]) < np.average(squares[7][6]):
        squares = np.rot90(squares, k=2)
    return chess.Board(), squares


def get_square_changes(board):
    """
    Given a board state return a list of tuples of square changes.
    The tuples correspond to the legal moves in the current position.
    """
    move_changes = []
    for move in board.legal_moves:
        print(move.from_square, move.to_square)
    return move_changes
