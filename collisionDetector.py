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

def main():
    import datetime
    from random import randint

    a_vertices = [(0, 0), (70, 0), (0, 70)]
    b_vertices = [(70, 70), (150, 70), (70, 150)]
    c_vertices = [(30, 30), (150, 70), (70, 150)]

    print("Triangle tests:")
    print("A and B:", collisionCheck(a_vertices, b_vertices))
    print("A and C:", collisionCheck(a_vertices, c_vertices))
    print("B and C:", collisionCheck(b_vertices, c_vertices))

    rect1 = [(25, 0), (25, 25), (50, 0), (50, 25)]
    rect2 = [(125, 0), (125, 25), (150, 0), (150, 25)]
    rect3 = [(45, 0), (45, 25), (130, 0), (130, 25)]

    print("")
    print("Rectangle tests:")
    print("r1 and r2:", collisionCheck(rect1, rect2))
    print("r1 and r3:", collisionCheck(rect1, rect3))
    print("r2 and r3:", collisionCheck(rect2, rect3))

    rect1 = [(20, 192), (41, 170), (87, 216), (65, 237)]
    rect2 = [(22, 174), (22, 155), (97, 155), (97, 174)]
    rect3 = [(75, 189), (75, 211), (112, 189), (112, 211)]

    print("")
    print("Rotated rectangle tests:")
    print("r1 and r2:", collisionCheck(rect1, rect2))
    print("r1 and r3:", collisionCheck(rect1, rect3))
    print("r2 and r3:", collisionCheck(rect2, rect3))

    print("")
    print("Performance test:")

    # Build objects
    shells = list()
    tanks = list()
    walls = list()
    for count in range(0, 25):
        shellX = randint(0, 500)
        shellY = randint(0, 500)
        shells.append([(shellX - 1, shellY - 1), (shellX - 1, shellY + 1), (shellX + 1, shellY - 1),
                       (shellX + 1, shellY + 1)])

        tankX = randint(0, 500)
        tankY = randint(0, 500)
        tanks.append([(tankX - 3, tankY - 3), (tankX - 3, tankY + 3), (tankX + 3, tankY - 3),
                       (tankX + 3, tankY + 3)])

    for count in range(0, 10):
        wallPosX = randint(0, 500)
        wallPosY = randint(0, 500)
        wallSizeX = randint(5, 50) / 2
        wallSizeY = randint(5, 50) / 2
        walls.append([(wallPosX - wallSizeX, wallPosY - wallSizeY), (wallPosX - wallSizeX, wallPosY + wallSizeY),
                      (wallPosX + wallSizeX, wallPosY - wallSizeY), (wallPosX + wallSizeX, wallPosY + wallSizeY)])

    # Now do the collision checking
    startTime = datetime.datetime.now()
    tankShellCollisions = 0
    wallShellCollisions = 0
    for shell in shells:
        didHitTank = False
        for tank in tanks:
            if collisionCheck(tank, shell, maxDist=6):
                tankShellCollisions += 1
                didHitTank = True

        if not didHitTank:
            for wall in walls:
                if collisionCheck(wall, shell, maxDist=37):
                    wallShellCollisions += 1

    tankWallCollisions = 0
    for tank in tanks:
        for wall in walls:
            if collisionCheck(tank, wall, maxDist=40):
                tankWallCollisions += 1

    endTime = datetime.datetime.now()
    print(str(tankShellCollisions) + "/25 tanks collided with shells")
    print(str(tankWallCollisions) + "/25 tanks collided with walls")
    print(str(wallShellCollisions) + "/25 shells collided with walls")
    print("Math done in " + str((endTime - startTime).total_seconds()) + " seconds ")
    # Target of 0.01 seconds to hit 60 FPS with margin I need

if __name__ == "__main__":
    main()