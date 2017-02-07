import math

# Utility functions for use by gameMaster

# Moves a game object the given distance along its current heading
#   The object must have the x, y, and heading properties
def moveObj(obj, distance):
    obj.x += math.cos(obj.heading) * distance
    obj.y += math.sin(obj.heading) * distance