import datetime
import math
import copy

import config

class tank:
    """
    Stores the state data for a tank
    """
    def __init__(self):
        self.x = -100           # Current x position
        self.y = -100           # Current y position
        self.heading = 0        # Current heading in radians from the +x axis
        self.moving = False     # Boolean for whether or not this tank is moving
        self.alive = False      # Boolean for whether or not this tank is alive

        # The datetime of this tank's last shot
        self.__lastShotTime = datetime.datetime.now() - datetime.timedelta(seconds=config.game.tank.reloadTime)

        self.kills = 0          # Kills in the current round
        self.wins = 0           # Rounds won

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
        myDict = copy.copy(self.__dict__)

        # The lastShotTime should never be in a gameState update
        del myDict["_tank__lastShotTime"]

        # Remove scores if this update needs to be cleaned
        if doClean:
            del myDict["kills"]
            del myDict["wins"]

        return myDict

    def toPoly(self):
        """
        :return: The tank's polygon as a list of points as tuples
        """
        halfWidth = config.game.tank.width / 2
        halfHeight = config.game.tank.height / 2
        return [(self.x - halfWidth, self.y - halfHeight), (self.x - halfWidth, self.y + halfHeight),
                (self.x + halfWidth, self.y - halfHeight), (self.x + halfWidth, self.y + halfHeight)]