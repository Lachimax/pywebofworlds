import numpy as np
import numpy.random as r
import math


def find_nearest(array, value):
    """
    Finds and returns the index in array of the closest entry to value.
    :param array: array to search
    :param value: number to search for
    :return: index in value of the closest number to value.
    """
    idx = np.searchsorted(array, value, side="left")
    if idx > 0 and (idx == len(array) or math.fabs(value - array[idx - 1]) < math.fabs(value - array[idx])):
        return idx - 1
    else:
        return idx


def prob_from_distribution(values, probabilities):
    """
    Produces a pseudorandom number given a custom probability distribution.
    The basis of this algorithm from:
    https://www.khanacademy.org/computing/computer-programming/programming-natural-simulations/programming-randomness/a/custom-distribution-of-random-numbers

    :param values: numpy array of values to be chosen from
    :param probabilities: normalised numpy array of probabilities
    :return: value chosen
    """
    if any(probabilities) > 1:
        raise ValueError('All values in the probabilities array must be less than or equal to 1')
    if probabilities.shape != values.shape:
        raise ValueError('The two arrays must be the same length')

    val = False

    while not val:
        # Pick a random number within the range of 'values'
        r1 = r.uniform(min(values), max(values))

        # Using probabilities array, assign a probability to this value
        idx = find_nearest(values, r1)
        p = probabilities[idx]

        # Pick another random num
        r2 = r.random()
        # print(str(r1) + ' ' + str(p) + ' ' + str(r1))

        if r2 < p:
            return r1


def perp_distance(point, line_point1, line_point2):
    """
    Returns the perpendicular distance between a point and a line defined by two other points. Formula derived from
    http://mathworld.wolfram.com/Point-LineDistance3-Dimensional.html
    :param point: a triple containing the x, y, z coordinates of the point.
    :param line_point1: a triple containing the x, y, z coordinates of the first point on the line
    :param line_point2: a triple containing the x, y, z coordinates of the second point on the line
    :return:
    """

    x0 = float(point[0])
    y0 = float(point[1])
    z0 = float(point[2])

    x1 = float(line_point1[0])
    y1 = float(line_point1[1])
    z1 = float(line_point1[2])

    x2 = float(line_point2[0])
    y2 = float(line_point2[1])
    z2 = float(line_point2[2])

    # A2 is used here because the numerator is twice the area of the triangle formed by the three points.
    # A2 = math.sqrt((-y0 * z2 - y1 * z0 + y1 * z2 + z0 * y2 + z1 * y0 + z1 * y2) ** 2 +
    #                (-(-x0 * z2 - x1 * z0 + x1 * z2 + z0 * x2 + z1 * x0 - z1 * x2)) ** 2 +
    #                (-x0 * y2 - x1 * y0 + x1 * y2 + y0 * x2 + y1 * x0 - y1 * x2) ** 2)

    A2 = math.sqrt((x0 * y1 - x0 * y2 - x1 * y0 + x1 * y2 + x2 * y0 - x2 * y1) ** 2 +
                   (-x0 * z1 + x0 * z2 + x1 * z0 - x1 * z2 - x2 * z0 + x2 * z1) ** 2 +
                   (y0 * z1 - y0 * z2 - y1 * z0 + y1 * z2 + y2 * z0 - y2 * z1)**2)

    return A2 / math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
