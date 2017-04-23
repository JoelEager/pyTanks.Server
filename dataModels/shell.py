import math

import config

# Stores the state data for a shell in flight
class shell:
    # Constructor
    #   tankId:     The clientID of the tank that shot the shell
    #   tankObj:    That tank's object
    #   heading:    The shell's heading
    def __init__(self, tankId, tankObj, heading):
        self.shooterId = tankId     # The id of the tank that shot it
        self.x = tankObj.x          # Current x position
        self.y = tankObj.y          # Current y position
        self.heading = heading      # Heading in radians from the +x axis

    # Moves the shell the given distance along its heading
    def move(self, distance):
        self.x += math.cos(self.heading) * distance
        self.y -= math.sin(self.heading) * distance

    # Returns the shell's polygon as a list of points as tuples
    def toPoly(self):
        halfWidth = config.game.shell.width / 2
        halfHeight = config.game.shell.height / 2
        return [(self.x - halfWidth, self.y - halfHeight), (self.x - halfWidth, self.y + halfHeight),
                (self.x + halfWidth, self.y - halfHeight), (self.x + halfWidth, self.y + halfHeight)]