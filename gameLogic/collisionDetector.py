"""
Performs collision detection on convex 2D polygons by means of the separating axis theorem (SAT)
    The contents of this file are based of off a Python implementation of SAT created by Juan Antonio Aldea Armenteros.
    The original version is available at https://github.com/JuantAldea/Separating-Axis-Theorem/. That code is under the
    GNU General Public License, but I (Joel Eager) have received written permission to distribute this modified version
    under the MIT license.
    
If this script is run as __main__ it will call perfTest() to perform a performance benchmark

Usage:
    export PYTHONPATH="../"
    python collisionDetector.py <numOfTrials>
"""

import math

import config

def hasCollided(poly1, poly2, maxDist=None):
    """
    Checks for a collision between two convex 2D polygons using separating axis theorem (SAT)
    :param poly1, poly2: The two polygons described as lists of points as tuples
        Example: [(x1, y1), (x2, y2), (x3, y3)]
        Note: The points list must go in sequence around the polygon
    :param maxDist: The maximum distance between any two points of any two polygons that can be touching
        If this is left off the optimization check that uses it will be skipped
    :return: The boolean result
    """
    def edgeVector(point1, point2):
        """
        :return: A vector going from point1 to point2
        """
        return point2[0] - point1[0], point2[1] - point1[1]

    def polyToEdges(poly):
        """
        Runs edgeVector() on each point paired with the point after it in the poly
        :return: A list of the edges of the poly as vectors
        """
        return [edgeVector(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]

    def orthogonal(vector):
        """
        :return: A vector which is at a right angle to the vector
        """
        return vector[1], - vector[0]

    def dotProduct(vector1, vector2):
        """
        :return: The dot (or scalar) product of the two vectors
        """
        return vector1[0] * vector2[0] + vector1[1] * vector2[1]

    def project(poly, axis):
        """
        :return: A vector showing how much of the poly lies along the axis
        """
        dots = [dotProduct(point, axis) for point in poly]
        return [min(dots), max(dots)]

    def overlap(projection1, projection2):
        """
        :return: Boolean indicating if the two projections overlap
        """
        return min(projection1) <= max(projection2) and min(projection2) <= max(projection1)

    def runSAT(poly1, poly2):
        """
        :return: The boolean result of running separating axis theorem on the two polys
        """
        edges = polyToEdges(poly1) + polyToEdges(poly2)
        axes = [orthogonal(edge) for edge in edges]

        for axis in axes:
            overlapping = overlap(project(poly1, axis), project(poly2, axis))
            if not overlapping:
                return False
        return True

    # Do an optimization check using the maxDist
    if maxDist is not None:
        if (poly1[1][0] - poly2[0][0]) ** 2 + (poly1[1][1] - poly2[0][1]) ** 2 <= maxDist ** 2:
            # Collision is possible so run SAT on the polys
            return runSAT(poly1, poly2)
        else:
            return False
    else:
        # No maxDist so run SAT on the polys
        return runSAT(poly1, poly2)

def getMaxDist(rect1, rect2):
    """
    Finds the maxDist for two rectangles that can be fed into hasCollided()
        To do so this function finds the maximum distance that can any two corners on two rectangles can be separated 
        by while the rectangles are touching.
    :param rect1, rect2: Objects or classes representing rectangles with width and height fields
    """
    rect1Size = math.sqrt(rect1.width ** 2 + rect1.height ** 2)
    rect2Size = math.sqrt(rect2.width ** 2 + rect2.height ** 2)

    return rect1Size + rect2Size

class maxDistValues:
    """
    Pre-calculated maxDist values for use when checking collisions between two objects with sizes set by config.py
    """
    tankShell = getMaxDist(config.game.tank, config.game.shell)
    tankTank = getMaxDist(config.game.tank, config.game.tank)

def perfTest(iterations):
    """
    Runs a speed benchmark on hasCollided() using a tank and shell and prints the results
    :param iterations: The number of times to repeat each test
    """
    import datetime
    from dataModels import tank, shell

    def runTrials(maxDist=None):
        """
        Runs the number of trials set by iterations
        :return: The time taken in seconds
        """
        # Set up the objects
        aTank = tank()
        aTank.x = 200
        aTank.y = 100
        aShell = shell(0, aTank, 0)

        # Run the trials
        start = datetime.datetime.now()
        for count in range(0, iterations):
            aShell.x = 100

            while not hasCollided(aTank.toPoly(), aShell.toPoly(), maxDist=maxDist):
                aShell.move(1)

        return (datetime.datetime.now() - start).total_seconds()

    def round(num, precision):
        """
        :return: num rounded to the given number of digits after the decimal
        """
        return math.ceil(num * (10 ** precision)) / (10 ** precision)

    print("Benchmarking hasCollided() using a shell and tank...")
    print("Using " + str(iterations) + " iterations\n")

    timeWith = runTrials(maxDist=maxDistValues.tankShell)
    timeWithout = runTrials()

    print("Time with maxDist: " + str(round(timeWith, 5)) + " secs")
    print("Time without:      " + str(round(timeWithout, 5)) + " secs\n")

    print("maxDist is " + str(round(timeWithout / timeWith, 2)) + " times faster")

# If this file is run just launch perfTest()
if __name__ == "__main__":
    import sys
    try:
        perfTest(int(sys.argv[1]))
    except (ValueError, IndexError):
        print("Usage: python collisionDetector.py <numOfTrials>")