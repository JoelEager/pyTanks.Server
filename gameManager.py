import copy
import json
from random import randint

import wsServer
import config
import gameClasses
import collisionDetector

# The logic for running the game and sending updates to clients
#   gameLoop() is called once per frame to run the game logic
#   updateClients() is called at the rate set in config.py for updating clients

# Lists for the current shells and walls
shells = list()
walls = list()

# Run the logic to maintain the game state and apply commands from player clients
#   (Called once every frame by wsServer.py)
#   elapsedTime:    The time elapsed in seconds since the last frame
def gameLoop(elapsedTime):
    # Temporary, per-frame lists
    players = list()        # A complete list of the clientIDs of players with alive tanks
    otherTanks = list()     # The list of stopped tanks and already moved tanks used by checkTankLocation()

    # Checks a tank's location against the map bounds, the otherTanks list, and the list of walls
    #   If the tank has collided with any of those it is moved back and the moving property is set to False
    def checkTankLocation(tankToCheck):
        def didCollide():
            tankToCheck.move(-config.gameSettings.tank.speed * elapsedTime)
            tankToCheck.moving = False

        # Check for collisions with map bounds
        for point in tankToCheck.toPoly():
            if (point[0] > config.gameSettings.map.width or point[0] < 0 or point[1] > config.gameSettings.map.height
                    or point[1] < 0):
                didCollide()
                return

        # Check for collisions with other tanks
        for otherTank in otherTanks:
            if collisionDetector.hasCollided(tankToCheck.toPoly(), otherTank.toPoly(),
                                             maxDist=collisionDetector.maxDistValues.tankTank):
                didCollide()
                return

        # Check for collisions with walls
        #for wall in walls:
        #    wallTank = collisionDetector.getMaxDist(tankToCheck, wall)
        #    if collisionDetector.hasCollided(player.tank.toPoly(), wall.toPoly(), maxDist=wallTank):
        #        didCollide()
        #        return
        # TODO: Uncomment and test once walls are implemented

    # Move the shells and check for collisions with the map bounds
    outOfBoundsShells = list()
    for index in range(0, len(shells)):
        shells[index].move(config.gameSettings.shell.speed * elapsedTime)

        # Discard any shells that fly off the map
        if (shells[index].x > config.gameSettings.map.width or shells[index].x < 0 or
                shells[index].y > config.gameSettings.map.height or shells[index].y < 0):
            outOfBoundsShells.insert(0, index)

    for index in outOfBoundsShells:
        del shells[index]

    # Fill the per-frame lists, execute any commands, and create tanks for new players
    for clientID in list(wsServer.clients.keys()):
        if wsServer.clients[clientID].type == config.serverSettings.clientTypes.player:
            player = wsServer.clients[clientID]

            if hasattr(player, "tank"):
                if player.tank.alive:
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

                        # If there's another queued command it'll be processed in the next frame

                    # Add stopped tanks to the list of otherTanks
                    if not player.tank.moving:
                        otherTanks.append(player.tank)

                    # Append the player's id to the list of players
                    players.append(clientID)
            else:
                # New player so initialize a tank
                halfWidth = (config.gameSettings.map.width / 2) - config.gameSettings.tank.width
                halfHeight = (config.gameSettings.map.height / 2) - config.gameSettings.tank.height
                player.tank = gameClasses.tank(halfWidth + randint(-halfWidth, halfWidth),
                                               halfHeight + randint(-halfHeight, halfHeight), 0)
                # TODO: Prevent spawning in invalid locations

                # TODO: Debugging code
                player.tank.alive = True

    # Update positions for any moving tanks and check for collisions on all tanks
    for clientID in players:
        tank = wsServer.clients[clientID].tank

        # Move the tank if it is moving
        if tank.moving:
            tank.move(config.gameSettings.tank.speed * elapsedTime)

        # Check if the tank is hit
        for index in range(0, len(shells)):
            shell = shells[index]
            # This if statement keeps a tank from being hit by it's own shell on the same frame as it shot that shell
            if shell.shooterId != clientID:
                if collisionDetector.hasCollided(tank.toPoly(), shell.toPoly(),
                                                 maxDist=collisionDetector.maxDistValues.tankShell):
                    # Mark tank as dead, give the shooter a kill, and delete the shell
                    tank.alive = False
                    tank.moving = False
                    wsServer.clients[shell.shooterId].tank.kills += 1
                    del shells[index]
                    break

        # Location checking is only needed for moving tanks
        if tank.moving:
            checkTankLocation(tank)
            otherTanks.append(tank)

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