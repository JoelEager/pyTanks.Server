import copy
import json

import wsServer
import config
import gameClasses

# The logic for running the game and sending updates to clients
#   gameLoop() is called once per frame to run the game logic
#   updateClients() is called at the rate set in config.py for updating clients

# Lists for the currently active shells and walls
shells = list()
walls = list()

# Run the logic to maintain the game state and apply commands from player clients
#   (Called once every frame by wsServer.py)
#   elapsedTime:    The time elapsed in seconds since the last frame
def gameLoop(elapsedTime):
    # Move the shells
    for index in range(0, len(shells)):
        shells[index].move(config.gameSettings.shellSpeed * elapsedTime)

        # Discard any shells that fly off the map
        if (shells[index].x > config.gameSettings.mapSize.x + 25 or shells[index].x < -25 or
            shells[index].y > config.gameSettings.mapSize.y + 25 or shells[index].y < -25):
            del shells[index]
            # Can't delete an item in the loop so break and then check the rest of the shells the next time around
            break

    # Process movement and commands for each player
    for clientID in list(wsServer.clients.keys()):
        if wsServer.clients[clientID].type == config.serverSettings.clientTypes.player:
            player = wsServer.clients[clientID]

            if hasattr(player, "tank"):
                # Update tank position
                if player.tank.moving:
                    player.tank.move(config.gameSettings.tankProps.speed * elapsedTime)
            else:
                # Initialize a tank if this a new player
                player.tank = gameClasses.tank(config.gameSettings.mapSize.x / 2, config.gameSettings.mapSize.x / 2, 0)

                # TODO: Debugging code
                player.tank.status = config.serverSettings.tankStatus.alive

            # Execute any commands
            if len(player.incoming) != 0:
                command = player.incoming.pop()

                if command.action == config.serverSettings.commands.fire:
                    if player.tank.canShoot(command.arrivalTime):
                        player.tank.didShoot()
                        shells.append(gameClasses.shell(clientID, player.tank, command.arg))
                    else:
                        wsServer.reportClientError(clientID, "Tank tried to shoot too quickly", False)
                elif command.action == config.serverSettings.commands.turn:
                    player.tank.heading = command.arg
                elif command.action == config.serverSettings.commands.stop:
                    player.tank.moving = False
                elif command.action == config.serverSettings.commands.go:
                    player.tank.moving = True

            # For now just kick any tanks that drive off the map
            # TODO: Kill them instead
            if (player.tank.x > config.gameSettings.mapSize.x + 25 or player.tank.x < -25 or
                player.tank.y > config.gameSettings.mapSize.y + 25 or player.tank.y < -25):
                    wsServer.reportClientError(clientID, "Tank fell off the map", True)

# Send game state updates to clients
#   (Called every time an update is due to be sent by wsServer.py)
def updateClients():
    # Generates JSON for a given object
    #   doClean - True/False to indicate if the dict should be cleaned for sending to players
    def generateJSON(rootObj, doClean):
        # Function for helping the json encoder in parsing objects
        def objToDict(obj):
            if isinstance(obj, gameClasses.tank):
                return obj.toDict(doClean)
            else:
                return obj.__dict__

        return json.dumps(objToDict(rootObj), default=objToDict, separators=(',', ':'))

    # Build a gameState object
    class gameState:
        def __init__(self):
            self.tanks = None
            self.shells = shells
            self.walls = walls

    currentGameState = gameState()

    # Build the tanks dict
    tanks = dict()
    for clientID in wsServer.clients:
        if wsServer.clients[clientID].type == config.serverSettings.clientTypes.player:
            aTank = copy.copy(wsServer.clients[clientID].tank)
            tanks[clientID] = aTank

    # Send out clean data to players
    tankIDs = list(tanks.keys())
    for playerID in tankIDs:
        # Append the current tank's data and name to currentGameState
        myTank = tanks[playerID]
        myTank.name = config.serverSettings.tankNames[playerID]
        currentGameState.myTank = myTank
        
        # Generate a list of tanks containing all but the current tank and add it to currentGameState
        del tanks[playerID]
        currentGameState.tanks = list(tanks.values())
        
        # Clean and send currentGameState to the current player
        wsServer.send(playerID, generateJSON(currentGameState, True))

        # Clean up currentGameState, myTank, and the cleanedTanks dict
        del currentGameState.myTank
        del myTank.name
        tanks[playerID] = myTank

    # Send complete data to the viewers
    for playerID in tankIDs:
        tanks[playerID].name = config.serverSettings.tankNames[playerID]
    currentGameState.tanks = list(tanks.values())
    wsServer.send(config.serverSettings.clientTypes.viewer, generateJSON(currentGameState, False))