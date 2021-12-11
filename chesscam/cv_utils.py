#
# Utilities for working with images.
#
import cv2 as cv
import numpy as np
from sklearn.linear_model import HuberRegressor


def img_resize(img, size):
    """Resize img to fit into a size * size box."""
    shape = list(np.shape(img))
    scale = size / max(shape)
    shape[0] *= scale
    shape[1] *= scale
    return cv.resize(img, (int(shape[1]), int(shape[0])))


def line_equation(line):
    """Calculate the slope-intercept form of line based on its two points."""
    slope = (line[1][1] - line[0][1]) / (line[1][0] - line[0][0])
    intercept = line[1][1] - (slope * line[1][0])
    return (slope, intercept)


def fit_line_in_rectangle(line, w, h):
    """
    Return two points at the borders of a w * h box that fit on line.
    The line is expected to be given in slope-intercept equation form.
    """
    slope, y_int = line
    # Normalize slopes too close to zero.
    if -0.00001 < slope < 0.00001:
        slope = np.copysign(0.00001, slope)
    x_int = -y_int / slope
    if x_int >= 0:
        p1 = (x_int, 0)
    else:
        p1 = (w, slope * w + y_int)
    if y_int >= 0:
        p2 = (0, y_int)
    else:
        p2 = ((h - y_int) / slope, h)
    return (p1, p2)


def points_distance(p1, p2):
    """Calculate the distance between two points."""
    return np.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def closest_among(points, pt, too_far=None):
    """
    Return the element from points closest to pt,
    except if it is farther than too_far.
    https://codereview.stackexchange.com/a/28210
    """
    deltas = points - pt
    dists = np.einsum('ij,ij->i', deltas, deltas)
    candidate = np.argmin(dists)
    if too_far and dists[candidate] >= too_far:
        return None
    return tuple(points[candidate])


def closest_on_line(line, pt):
    """
    Return the point on line closest to pt.
    https://stackoverflow.com/a/47198877
    """
    x1, y1 = line[0]
    x2, y2 = line[1]
    x3, y3 = pt
    dx, dy = x2 - x1, y2 - y1
    det = dx * dx + dy * dy
    a = (dy * (y3 - y1) + dx * (x3 - x1)) / det
    return (x1 + a * dx, y1 + a * dy)


def intersect_lines(line1, line2):
    """Return the intersection point of two lines."""
    m1, b1 = line1
    m2, b2 = line2
    xi = (b1 - b2) / (m2 - m1)
    yi = m1 * xi + b1
    return (xi, yi)


def linear_fit(points):
    """Fit a line on the points and return its slope-intercept form."""
    return np.polyfit(*zip(*points), 1)


# TODO: Scale down data instead of increasing iterations.
# https://scikit-learn.org/stable/modules/preprocessing.html
# TODO: Use custom Huber algorithm, from numpy, without sklearn.
def linear_fit_robust(points):
    """Use a robust linear fit algorithm."""
    x, y = map(np.array, zip(*points))
    huber = HuberRegressor(max_iter=1000, epsilon=2.0).fit(x.reshape(-1, 1), y)
    return (huber.coef_[0], huber.intercept_)


def perspective(points):
    """https://math.stackexchange.com/a/1630886"""
    diffs = [points_distance(*points[i:i+2]) for i in range(len(points) - 1)]
    ratios = [diffs[i+1] / diffs[i] for i in range(len(diffs) - 1)]
    ratio = np.mean(ratios)
    if ratio == 1:  # Avoid special case.
        ratio = np.nextafter(np.float32(ratio), 2)
    distsum = points_distance(points[0], points[-1])
    dist1 = (distsum * (1 - ratio))
    dist2 = (1 - ratio ** len(diffs))
    dist3 = ratio ** len(diffs)
    dist = (dist1 / dist2) * dist3
    t = (distsum + dist) / distsum
    x0, y0 = points[0]
    x1, y1 = points[-1]
    return ((1 - t) * x0 + t * x1, (1 - t) * y0 + t * y1)
