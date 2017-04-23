import datetime
import math
import copy

import config

# Stores the state data for a tank
class tank:
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

    # Used to cap rate of fire
    #   returns: True if the tank can shoot, False if not
    def canShoot(self, timeOfShot):
        marginOfError = 0.2  # Used to account for network issues throwing off the timing
        return datetime.timedelta(seconds=config.game.tank.reloadTime - marginOfError) <= \
            timeOfShot - self.__lastShotTime

    # Called whenever a tank shoots so its lastShotTime can be updated
    def didShoot(self):
        self.__lastShotTime = datetime.datetime.now()

    # Moves the tank the given distance along its current heading
    def move(self, distance):
        self.x += math.cos(self.heading) * distance
        self.y -= math.sin(self.heading) * distance

    # Returns a dict of the tank's data
    #   doClean:    True/False to indicate if the dict should be cleaned for sending to players
    def toDict(self, doClean):
        myDict = copy.copy(self.__dict__)

        # The lastShotTime should never be in a gameState update
        del myDict["_tank__lastShotTime"]

        # Remove scores if this update needs to be cleaned
        if doClean:
            del myDict["kills"]
            del myDict["wins"]

        return myDict

    # Returns the tank's polygon as a list of points as tuples
    def toPoly(self):
        halfWidth = config.game.tank.width / 2
        halfHeight = config.game.tank.height / 2
        return [(self.x - halfWidth, self.y - halfHeight), (self.x - halfWidth, self.y + halfHeight),
                (self.x + halfWidth, self.y - halfHeight), (self.x + halfWidth, self.y + halfHeight)]