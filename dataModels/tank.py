import datetime
import math
import copy

import config

class tank:
    """
    Stores the state data for a tank
    """
    def __init__(self):
        self.x = -100           # Current x position of the tank's center
        self.y = -100           # Current y position of the tank's center
        self.heading = 0        # Current heading in radians from the +x axis
        self.moving = False     # Boolean for whether or not this tank is moving
        self.alive = False      # Boolean for whether or not this tank is alive

        # The datetime of this tank's last shot
        self.__lastShotTime = datetime.datetime.now() - datetime.timedelta(seconds=config.game.tank.reloadTime)

        self.kills = 0          # Kills in the current round
        self.wins = 0           # Rounds won

        # The string identifying this player's author or other info
        self.info = "This player has not provided any info."

    def spawn(self):
        """
        Resets the tank's per-game variables (other than position)
        """
        self.heading = 0
        self.moving = False
        self.alive = True
        self.__lastShotTime = datetime.datetime.now() - datetime.timedelta(seconds=config.game.tank.reloadTime)
        self.kills = 0

    def canShoot(self):
        """
        Used to cap rate of fire
        :return: True if the tank can shoot, False if not
        """
        return datetime.timedelta(seconds=config.game.tank.reloadTime) <= datetime.datetime.now() - self.__lastShotTime

    def didShoot(self):
        """
        Called whenever a tank shoots so its lastShotTime can be updated
        """
        self.__lastShotTime = datetime.datetime.now()

    def move(self, distance):
        """
        Moves the tank the given distance along its current heading
        """
        self.x += math.cos(self.heading) * distance
        self.y -= math.sin(self.heading) * distance

    def toDict(self, doClean):
        """
        :param doClean: True/False to indicate if the dict should be cleaned for sending to players
        :return: A dictionary of the tank's data
        """
        myDict = copy.copy(vars(self))

        # The lastShotTime should never be in a gameState update
        del myDict["_tank__lastShotTime"]

        # Remove info that should be hidden from players
        if doClean:
            del myDict["kills"]
            del myDict["wins"]
            del myDict["info"]

        return myDict

    def to_poly(self, margin=0):
        """
        :param margin: If set the polygon will have a padding of margin pixels in every direction
        :return: The tank's polygon as a list of points as tuples
        """
        sin = math.sin(self.heading)
        cos = math.cos(self.heading)

        def rotateVector(x, y):
            return x * cos - y * sin, x * sin + y * cos

        halfWidth = (config.game.tank.width / 2) + margin
        halfHeight = (config.game.tank.height / 2) + margin
        poly = [rotateVector(-halfWidth, -halfHeight),
                rotateVector(halfWidth, -halfHeight),
                rotateVector(halfWidth, halfHeight),
                rotateVector(-halfWidth, halfHeight)]

        for count in range(0, len(poly)):
            vector = poly[count]
            poly[count] = (vector[0] + self.x, vector[1] + self.y)

        return poly
