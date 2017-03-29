import math
import copy
import datetime
from random import randint

import config

# Classes used to store game state data

# Stores the state data for one tank along with the status and score for its ai
class tank:
    # Constructor
    #   x, y, heading:  The initial position and heading for the tank
    def __init__(self):
        self.x = -100               # Current x position
        self.y = -100               # Current y position
        self.heading = 0            # Current heading in radians from the +x axis
        self.moving = False         # Boolean for whether or not this tank is moving
        self.alive = False          # Boolean for whether or not this tank is alive

        # The datetime of this tank's last shot
        self.__lastShotTime = datetime.datetime.now() - datetime.timedelta(seconds=config.game.tank.reloadTime)

        self.kills = 0              # Kills in the current round
        self.wins = 0               # Rounds won

    # Checks if this tank can shoot
    #   If shots are fired faster than this the server will kick the player
    #   returns: True if the tank can shoot, False if not
    def canShoot(self, timeOfShot):
        marginOfError = 0.2     # Used to account for network issues throwing off the timing
        return datetime.timedelta(seconds=config.game.tank.reloadTime - marginOfError) <= timeOfShot - \
                                                                                          self.__lastShotTime
    
    # Called whenever a tank shoots so its __lastShotTime can be updated
    def didShoot(self):
        self.__lastShotTime = datetime.datetime.now()

    # Moves the tank the given distance along its current heading
    def move(self, distance):
        self.x += math.cos(self.heading) * distance
        self.y += math.sin(self.heading) * distance

    # Returns a dict of the tank's data
    #   doClean:    True/False to indicate if the dict should be cleaned for sending to players
    def toDict(self, doClean):
        myDict = copy.copy(self.__dict__)

        # The __lastShotTime should never be in a gameState update
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

# Stores the state data for a shell in flight
class shell:
    # Constructor
    #   tankId, tankObj:    The clientID and object of the tank that shot the shell
    def __init__(self, tankId, tankObj, heading):
        self.shooterId = tankId     # The id of the tank that shot it
        self.x = tankObj.x          # Current x position
        self.y = tankObj.y          # Current y position
        self.heading = heading      # Heading in radians from the +x axis

    # Moves the shell the given distance along its heading
    def move(self, distance):
        self.x += math.cos(self.heading) * distance
        self.y += math.sin(self.heading) * distance
    
    # Returns the shell's polygon as a list of points as tuples
    def toPoly(self):
        halfWidth = config.game.shell.width / 2
        halfHeight = config.game.shell.height / 2
        return [(self.x - halfWidth, self.y - halfHeight), (self.x - halfWidth, self.y + halfHeight), 
                (self.x + halfWidth, self.y - halfHeight), (self.x + halfWidth, self.y + halfHeight)]

# Stores the state data for a block of cover on the map
class wall:
    def __init__(self):
        # Set lengths for the long and short sides of the wall
        longSide = randint(config.game.wall.longSideBounds[0], config.game.wall.longSideBounds[1])
        shortSide = randint(config.game.wall.shortSideBounds[0], config.game.wall.shortSideBounds[1])

        # Decide if this is going to be a tall or long wall
        if randint(0, 2) == 0:
            self.width, self.height = longSide, shortSide
            self.x = randint(config.game.wall.placementPadding, config.game.map.width -
                             config.game.wall.placementPadding - config.game.wall.longSideBounds[0])
            self.y = randint(config.game.wall.placementPadding, config.game.map.height -
                             config.game.wall.placementPadding - config.game.wall.shortSideBounds[0])
        else:
            self.height, self.width = longSide, shortSide
            self.y = randint(config.game.wall.placementPadding, config.game.map.height -
                             config.game.wall.placementPadding - config.game.wall.longSideBounds[0])
            self.x = randint(config.game.wall.placementPadding, config.game.map.width -
                             config.game.wall.placementPadding - config.game.wall.shortSideBounds[0])

        # Check to make sure the wall doesn't go too far
        if self.x + self.width > config.game.map.width - config.game.wall.placementPadding:
            self.width = config.game.map.width - config.game.wall.placementPadding - self.x
        elif self.y + self.height > config.game.map.height - config.game.wall.placementPadding:
            self.height = config.game.map.height - config.game.wall.placementPadding - self.y

        # Correct x and y to be the center of the wall instead of top-left corner
        self.x += self.width / 2
        self.y += self.height / 2

    # Returns the wall's polygon as a list of points as tuples
    #   margin:     If set the polygon will be larger by 2 * margin in every direction
    def toPoly(self, margin=0):
        halfWidth = self.width / 2
        halfHeight = self.height / 2
        return [(self.x - halfWidth - margin, self.y - halfHeight - margin),
                (self.x - halfWidth - margin, self.y + halfHeight + margin),
                (self.x + halfWidth + margin, self.y - halfHeight - margin),
                (self.x + halfWidth + margin, self.y + halfHeight + margin)]