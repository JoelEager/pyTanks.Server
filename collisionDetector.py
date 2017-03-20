# Performs collision detection on convex 2D polygons by means of the Separating axis theorem (SAT)
#   The contents of this file are based of off a python implementation of SAT created by JuantAldea. The original
#   version is available at https://github.com/JuantAldea/Separating-Axis-Theorem/. That code is under the GNU General
#   Public License, but I (Joel Eager) have received written permission to distribute this modified version under the
#   MIT license.

# Checks for a collision between two polygons using SAT
#   poly1, poly2:   The two polygons described as lists of points as tuples (Example: [(x1, y1), (x2, y2), (x3, y3)])
#   maxDist:        The maximum distance between any two points of any two polygons that can be touching
#                   (If this is left of the optimization check that uses it will be skipped)
def collisionCheck(poly1, poly2, maxDist=None):
    from math import sqrt

    def normalizeVector(vector):
        norm = sqrt(vector[0] ** 2 + vector[1] ** 2)
        return vector[0] / norm, vector[1] / norm

    def dotProduct(vector1, vector2):
        return vector1[0] * vector2[0] + vector1[1] * vector2[1]

    def edgeDirection(vector1, vector2):
        return vector2[0] - vector1[0], vector2[1] - vector1[1]

    def orthogonal(vector):
        return vector[1], - vector[0]

    def verticesToEdges(vertices):
        return [edgeDirection(vertices[i], vertices[(i + 1) % len(vertices)]) for i in range(len(vertices))]

    def project(vertices, axis):
        dots = [dotProduct(vertex, axis) for vertex in vertices]
        return [min(dots), max(dots)]

    def contains(n, rangeVector):
        a = rangeVector[0]
        b = rangeVector[1]
        if b < a:
            a = rangeVector[1]
            b = rangeVector[0]
        return (n >= a) and (n <= b)

    def overlap(a, b):
        if contains(a[0], b):
            return True
        if contains(a[1], b):
            return True
        if contains(b[0], a):
            return True
        if contains(b[1], a):
            return True
        return False

    def runSAT(vertices_a, vertices_b):
        edges_a = verticesToEdges(vertices_a)
        edges_b = verticesToEdges(vertices_b)

        edges = edges_a + edges_b

        axes = [normalizeVector(orthogonal(edge)) for edge in edges]

        for i in range(len(axes)):
            projection_a = project(vertices_a, axes[i])
            projection_b = project(vertices_b, axes[i])
            overlapping = overlap(projection_a, projection_b)
            if not overlapping:
                return False
        return True

    # Do an optimization check using the maxDist
    if maxDist is not None:
        if sqrt((poly1[1][0] - poly2[0][0]) ** 2 + (poly1[1][1] - poly2[0][1]) ** 2) <= maxDist:
            # Collision is possible so run SAT on the polys
            return runSAT(poly1, poly2)
        else:
            return False
    else:
        # No maxDist so run SAT on the polys
        return runSAT(poly1, poly2)