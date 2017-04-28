import math

import config

class shell:
    """
    Stores the state data for a shell in flight
    """
    def __init__(self, tankId, tankObj, heading):
        """
        Constructor
        :param tankId: The clientID of the tank that shot the shell
        :param tankObj: That tank's object
        :param heading: The shell's heading
        """
        self.shooterId = tankId     # The id of the tank that shot it
        self.x = tankObj.x          # Current x position
        self.y = tankObj.y          # Current y position
        self.heading = heading      # Heading in radians from the +x axis

    def move(self, distance):
        """
        Moves the shell the given distance along its heading
        """
        self.x += math.cos(self.heading) * distance
        self.y -= math.sin(self.heading) * distance

    def toPoly(self):
        """
        :return: The shell's polygon as a list of points as tuples
        """
        halfWidth = config.game.shell.width / 2
        halfHeight = config.game.shell.height / 2
        return [(self.x - halfWidth, self.y - halfHeight), (self.x - halfWidth, self.y + halfHeight),
                (self.x + halfWidth, self.y - halfHeight), (self.x + halfWidth, self.y + halfHeight)]