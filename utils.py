import math
import json

# Utility functions for use by gameMaster

# Moves a game object the given distance along its current heading
#   The object must have the x, y, and heading properties
def moveObj(obj, distance):
    obj.x += math.cos(obj.heading) * distance
    obj.y += math.sin(obj.heading) * distance

# Generates JSON for a given object
#   Any non-standard objects will be parsed using their __dict__ attribute
def generateJSON(obj):
    # Function for helping the json encoder in parsing objects
    def objHandler(Obj):
        return Obj.__dict__

    return json.dumps(objHandler(obj), default=objHandler, separators=(',', ':'))