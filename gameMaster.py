import json
import math
import copy
import wsServer
import config
import utils

# Main script of the pyTanks server
#   This script starts wsServer.py with a callback to its gameLoop() function
#   The gameLoop() function is called once a frame so it can maintain the game state

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

# Stores the state data for a shell in flight
class shell:
    def __init__(self, tankId, x, y, heading):
        self.shooterId = tankId # The id of the tank that shot it
        self.x = x              # Current x position
        self.y = y              # Current y position
        self.heading = heading  # Heading in radians from the +x axis

# Stores the state data for a block of cover on the map
class cover:
    def __init__(self, x, y, width, height):
        self.x = x              # X position
        self.y = y              # Y position
        self.width = width      # Width
        self.height = height    # Height

# Lists for the currently active shells and cover blocks
shells = list()
coverBlocks = list()

# Run the logic to maintain the game state and apply commands from player clients
#   (Called once every frame by wsServer.py)
#   elapsedTime:    The time elapsed in seconds since the last frame
def gameLoop(elapsedTime):
    for clientID in wsServer.clients:
        aClient = wsServer.clients[clientID]

        if aClient.type == config.serverSettings.clientTypes.player:
            if hasattr(aClient, 'tank'):
                # Update tank positions
                if aClient.tank.status == config.serverSettings.tankStatus.alive and aClient.tank.moving:
                    utils.moveObj(aClient.tank, config.gameSettings.tankProps.speed * elapsedTime)
            else:
                # Initialize a tank for any new players
                aClient.tank = tank(100, 100, math.pi / 4)

                # TODO: Debugging code
                aClient.tank.status = config.serverSettings.tankStatus.alive
                aClient.tank.moving = True

            # Check for commands
            if len(aClient.incoming) != 0:
                message = aClient.incoming.pop()
                if message == "change_heading":
                    aClient.tank.heading += math.pi / 2

# Send game state updates to clients
#   (Called every time an update is due to be sent by wsServer.py)
def updateClients():
    # Function for helping the json encoder in parsing objects
    def objHandler(Obj):
        return Obj.__dict__

    # Build a gameState object to send out
    class gameState:
        def __init__(self):
            self.tanks = list()
            self.shells = shells
            self.coverBlocks = coverBlocks
    currentGameState = gameState()

    # Append the tanks
    for clientID in wsServer.clients:
        if wsServer.clients[clientID].type == config.serverSettings.clientTypes.player:
            aTank = copy.copy(wsServer.clients[clientID].tank)
            aTank.id = clientID     # TODO: Change to user-facing name
            currentGameState.tanks.append(aTank)

    # TODO: Send out cleaned data to players
    wsServer.sendAll(json.dumps(objHandler(currentGameState), default=objHandler, separators=(',', ':')))

# Start the server with references to the callback functions
wsServer.runServer(gameLoop, updateClients)