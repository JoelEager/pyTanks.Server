"""
Performs collision detection on convex 2D polygons by means of the separating axis theorem (SAT)
    The contents of this file are based of off a Python implementation of SAT created by Juan Antonio Aldea Armenteros.
    The original version is available at https://github.com/JuantAldea/Separating-Axis-Theorem/. That code is under the
    GNU General Public License, but I (Joel Eager) have received written permission to distribute this modified version
    under the MIT license.
    
If this script is run as __main__ it will call perfTest() to perform a performance benchmark

Usage:
    export PYTHONPATH="../"
    python collision_detector.py <numOfTrials>
"""

import math

import config


def has_collided(poly1, poly2, max_dist=None):
    """
    Checks for a collision between two convex 2D polygons using separating axis theorem (SAT)
    :param poly1, poly2: The two polygons described as lists of points as tuples
        Example: [(x1, y1), (x2, y2), (x3, y3)]
        Note: The points list must go in sequence around the polygon
    :param max_dist: The maximum distance between any two points of any two polygons that can be touching
        If this is left off the optimization check that uses it will be skipped
    :return: The boolean result
    """

    def edge_vector(point1, point2):
        """
        :return: A vector going from point1 to point2
        """
        return point2[0] - point1[0], point2[1] - point1[1]

    def poly_to_edges(poly):
        """
        Runs edgeVector() on each point paired with the point after it in the poly
        :return: A list of the edges of the poly as vectors
        """
        return [edge_vector(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]

    def orthogonal(vector):
        """
        :return: A new vector which is orthogonal to the given vector
        """
        return vector[1], - vector[0]

    def dot_product(vector1, vector2):
        """
        :return: The dot (or scalar) product of the two vectors
        """
        return vector1[0] * vector2[0] + vector1[1] * vector2[1]

    def project(poly, axis):
        """
        :return: A vector showing how much of the poly lies along the axis
        """
        dots = [dot_product(point, axis) for point in poly]
        return min(dots), max(dots)

    def overlap(projection1, projection2):
        """
        :return: Boolean indicating if the two projections overlap
        """
        return min(projection1) <= max(projection2) and min(projection2) <= max(projection1)

    def run_sat(poly1, poly2):
        """
        :return: The boolean result of running separating axis theorem on the two polys
        """
        edges = poly_to_edges(poly1) + poly_to_edges(poly2)
        axes = [orthogonal(edge) for edge in edges]

        for axis in axes:
            overlapping = overlap(project(poly1, axis), project(poly2, axis))

            if not overlapping:
                # The polys don't overlap on this axis so they can't be touching
                return False

        # The polys overlap on all axes so they must be touching
        return True

    # Do an optimization check using the max_dist
    if max_dist is not None:
        if (poly1[1][0] - poly2[0][0]) ** 2 + (poly1[1][1] - poly2[0][1]) ** 2 <= max_dist ** 2:
            # Collision is possible so run SAT on the polys
            return run_sat(poly1, poly2)
        else:
            return False
    else:
        # No max_dist so run SAT on the polys
        return run_sat(poly1, poly2)


def get_max_dist(rect1, rect2):
    """
    Finds the max_dist for two rectangles that can be fed into hasCollided()
        To do so this function finds the maximum distance that can any two corners on two rectangles can be separated 
        by while the rectangles are touching.
    :param rect1, rect2: Objects or classes representing rectangles with width and height fields
    """
    rect1_size = math.sqrt(rect1.width ** 2 + rect1.height ** 2)
    rect2_size = math.sqrt(rect2.width ** 2 + rect2.height ** 2)

    return rect1_size + rect2_size


class MaxDistValues:
    """
    Pre-calculated max_dist values for use when checking collisions between two objects with sizes set by config.py
    """
    tankShell = get_max_dist(config.game.tank, config.game.shell)
    tankTank = get_max_dist(config.game.tank, config.game.tank)


def perf_test(iterations):
    """
    Runs a speed benchmark on hasCollided() using a tank and shell and prints the results
    :param iterations: The number of times to repeat each test
    """
    import datetime

    from dataModels import tank, shell

    def run_trials(max_dist=None):
        """
        Runs the number of trials set by iterations
        :return: The time taken in seconds
        """
        # Set up the objects
        a_tank = tank()
        a_tank.x = 200
        a_tank.y = 100
        a_shell = shell(0, a_tank, 0)

        # Run the trials
        start = datetime.datetime.now()
        for count in range(0, iterations):
            a_shell.x = 100

            while not has_collided(a_tank.to_poly(), a_shell.toPoly(), max_dist=max_dist):
                a_shell.move(1)

        return (datetime.datetime.now() - start).total_seconds()

    print("Running has_collided() through {} iterations...".format(iterations))
    print("Completed in {} seconds".format(run_trials()))


# If this file is run just launch perfTest()
if __name__ == "__main__":
    import sys

    try:
        perf_test(int(sys.argv[1]))
    except (ValueError, IndexError):
        print("Usage: python collision_detector.py <numOfTrials>")
