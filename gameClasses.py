import math
import config
import copy

# Classes used to store game state data

# Stores the state data for one tank along with the status and score for its ai
class tank:
    def __init__(self, x, y, heading):
        self.x = x              # Current x position
        self.y = y              # Current y position
        self.heading = heading  # Current heading in radians from the +x axis
        self.moving = False      # Boolean for whether or not this tank is moving

        # Current status for this tank
        self.status = config.serverSettings.tankStatus.dead

        self.kills = 0          # For the current round
        self.wins = 0           # Rounds won

    # Moves the tank the given distance along its current heading
    def move(self, distance):
        self.x += math.cos(self.heading) * distance
        self.y += math.sin(self.heading) * distance

    # Returns a dict of the tank's data
    #   doClean - True/False to indicate if the dict should be cleaned for sending to players
    def toDict(self, doClean):
        myDict = copy.copy(self.__dict__)

        if doClean:
            del myDict["kills"]
            del myDict["wins"]

        return myDict

# Stores the state data for a shell in flight
class shell:
    def __init__(self, tankId, x, y, heading):
        self.shooterId = tankId # The id of the tank that shot it
        self.x = x              # Current x position
        self.y = y              # Current y position
        self.heading = heading  # Heading in radians from the +x axis

    # Moves the shell the given distance along its heading
    def move(self, distance):
        self.x += math.cos(self.heading) * distance
        self.y += math.sin(self.heading) * distance

# Stores the state data for a block of cover on the map
class wall:
    def __init__(self, x, y, width, height):
        self.x = x              # X position
        self.y = y              # Y position
        self.width = width      # Width
        self.height = height    # Height