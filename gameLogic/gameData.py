"""
Holds the game's data structures and the functions for interacting with them
"""

import json
import copy

import config
from serverLogic import serverData
from dataModels import tank

shells = list()         # The list of shells currently in flight
walls = list()          # The list of walls on the map

playerCount = 0         # The current number of connected players
ongoingGame = False     # Is there a game in progress currently?

def updateClients():
    """
    Sends game state updates to clients
        Called every time an update is due to be sent by gameClock.py
    """
    def generateJSON(gameStateObj, doClean):
        """
        Generates JSON for a given object
        :param rootObj: The object to encode
        :param doClean: True/False to indicate if the dict should be cleaned for sending to players
        """
        def objToDict(obj):
            """
            Helps the json encoder in parsing objects
            """
            if isinstance(obj, tank):
                if doClean and not hasattr(obj, "name"):
                    return obj.toDict(True)
                else:
                    return obj.toDict(False)
            else:
                return vars(obj)

        return json.dumps(objToDict(gameStateObj), default=objToDict, separators=(',', ':'))

    # Build a gameState object
    class gameState:
        def __init__(self):
            self.ongoingGame = ongoingGame
            self.tanks = None
            self.shells = shells
            self.walls = walls

    currentGameState = gameState()

    # Build the tanks dict
    tanks = dict()
    for clientID in serverData.clients:
        if serverData.clients[clientID].isPlayer():
            aTank = copy.copy(serverData.clients[clientID].tank)
            aTank.id = clientID
            tanks[clientID] = aTank

    # Send out clean data to players
    #   Note: This loop iterates over a list of keys to prevent it from being messed up by adding and removing keys
    for playerID in list(tanks.keys()):
        # Append the current tank's data and name to currentGameState
        myTank = tanks[playerID]
        myTank.name = config.server.tankNames[playerID]
        myTank.canShoot = myTank.canShoot()
        currentGameState.myTank = myTank

        # Generate a dictionary of tanks containing all but the current tank and add it to currentGameState
        del tanks[playerID]
        currentGameState.tanks = list(tanks.values())

        # Clean and send currentGameState to the current player
        serverData.send(playerID, generateJSON(currentGameState, True))

        # Clean up currentGameState, myTank, and the cleanedTanks dict
        del currentGameState.myTank
        del myTank.name
        del myTank.canShoot
        tanks[playerID] = myTank

    # Send complete data to the viewers
    for playerID in tanks.keys():
        del tanks[playerID].id
        tanks[playerID].name = config.server.tankNames[playerID]
    
    currentGameState.tanks = list(tanks.values())
    serverData.send(config.server.clientTypes.viewer, generateJSON(currentGameState, False))