from random import randint

import config
from . import collisionDetector, gameData
import dataModels
from serverLogic import serverData

# The logic for running the game and sending updates to clients

# Starts a new game
def startGame():
    gameData.shells = list()
    gameData.walls = list()

    # Create the walls
    for count in range(0, randint(5, 10)):
        isValidLocation = False
        aWall = None
        while not isValidLocation:
            aWall = dataModels.wall()
            isValidLocation = True

            # Check for overlap with the other walls
            for otherWall in gameData.walls:
                if collisionDetector.hasCollided(aWall.toPoly(), otherWall.toPoly(
                        margin=config.game.wall.placementPadding)):
                    isValidLocation = False
                    break

        gameData.walls.append(aWall)

    # Spawn the tanks
    halfWidth = (config.game.map.width / 2) - config.game.tank.width
    halfHeight = (config.game.map.height / 2) - config.game.tank.height
    tanksSpawned = list()
    for clientID in list(serverData.clients.keys()):
        if serverData.clients[clientID].isPlayer():
            tank = serverData.clients[clientID].tank

            tank.heading = 0
            tank.moving = False
            tank.alive = True
            tank.kills = 0

            isValidLocation = False
            while not isValidLocation:
                tank.x = (config.game.map.width / 2) + randint(-halfWidth, halfWidth)
                tank.y = (config.game.map.height / 2) + randint(-halfHeight, halfHeight)
                isValidLocation = True

                # Check for collisions with the walls
                for wall in gameData.walls:
                    if collisionDetector.hasCollided(tank.toPoly(), wall.toPoly()):
                        isValidLocation = False
                        break

                # Check for collisions with the other tanks
                for otherTank in tanksSpawned:
                    if collisionDetector.hasCollided(tank.toPoly(), otherTank.toPoly()):
                        isValidLocation = False
                        break

            tanksSpawned.append(tank)

    # Start the game
    gameData.ongoingGame = True

# Runs the logic to maintain the game state and applies commands from players
#   (Called once every frame by gameClock.py)
#   elapsedTime:    The time elapsed, in seconds, since the last frame
def gameTick(elapsedTime):
    # Temporary, per-frame lists
    players = list()        # A complete list of the clientIDs of players with alive tanks
    otherTanks = list()     # The list of stopped tanks and already moved tanks used by checkTankLocation()

    # Checks a tank's location against the map bounds, the otherTanks list, and the list of walls
    #   If the tank has collided with any of those it is moved back and the moving property is set to False
    def checkTankLocation(tankToCheck):
        def didCollide():
            tankToCheck.move(-config.game.tank.speed * elapsedTime)
            tankToCheck.moving = False

        # Check for collisions with map bounds
        for point in tankToCheck.toPoly():
            if (point[0] > config.game.map.width or point[0] < 0 or point[1] > config.game.map.height
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
        for wall in gameData.walls:
            if collisionDetector.hasCollided(tankToCheck.toPoly(), wall.toPoly()):
                didCollide()
                return

    # Move the shells and check for collisions with the map bounds
    outOfBoundsShells = list()
    for index in range(0, len(gameData.shells)):
        gameData.shells[index].move(config.game.shell.speed * elapsedTime)

        # Discard any shells that fly off the map
        if (gameData.shells[index].x > config.game.map.width or gameData.shells[index].x < 0 or
                gameData.shells[index].y > config.game.map.height or gameData.shells[index].y < 0):
            outOfBoundsShells.insert(0, index)
            continue

        # Discard any shells that hit a wall
        for wall in gameData.walls:
            if collisionDetector.hasCollided(gameData.shells[index].toPoly(), wall.toPoly()):
                outOfBoundsShells.insert(0, index)
                break

    for index in outOfBoundsShells:
        del gameData.shells[index]

    # Fill the per-frame lists, execute any commands, and create tanks for new players
    for clientID in list(serverData.clients.keys()):
        if serverData.clients[clientID].isPlayer():
            player = serverData.clients[clientID]

            if player.tank.alive:
                # Execute any commands
                if len(player.incoming) != 0:
                    command = player.incoming.pop()

                    if command.action == config.server.commands.fire:
                        if player.tank.canShoot(command.arrivalTime):
                            player.tank.didShoot()
                            gameData.shells.append(dataModels.shell(clientID, player.tank, command.arg))
                        else:
                            serverData.reportClientError(clientID, "Tank tried to shoot too quickly", False)
                    elif command.action == config.server.commands.turn:
                        player.tank.heading = command.arg
                    elif command.action == config.server.commands.stop:
                        player.tank.moving = False
                    elif command.action == config.server.commands.go:
                        player.tank.moving = True

                    # If there's another queued command it'll be processed in the next frame

                # Add stopped tanks to the list of otherTanks
                if not player.tank.moving:
                    otherTanks.append(player.tank)

                # Append the player's id to the list of players
                players.append(clientID)

    # Update positions for any moving tanks and check for collisions on all tanks
    for clientID in players:
        tank = serverData.clients[clientID].tank

        # Move the tank if it is moving
        if tank.moving:
            tank.move(config.game.tank.speed * elapsedTime)

        # Check if the tank is hit
        for index in range(0, len(gameData.shells)):
            shell = gameData.shells[index]
            # This if statement keeps a tank from being hit by it's own shell on the same frame as it shot that shell
            if shell.shooterId != clientID:
                if collisionDetector.hasCollided(tank.toPoly(), shell.toPoly(),
                                                 maxDist=collisionDetector.maxDistValues.tankShell):
                    # Mark tank as dead, give the shooter a kill, and delete the shell
                    tank.alive = False
                    tank.moving = False
                    serverData.clients[shell.shooterId].tank.kills += 1
                    del gameData.shells[index]
                    break

        # Location checking is only needed for moving tanks
        if tank.moving:
            checkTankLocation(tank)
            otherTanks.append(tank)

    if len(players) == 1:
        # We have a winner!
        serverData.clients[players[0]].tank.wins += 1
        serverData.clients[players[0]].tank.alive = False
        gameData.ongoingGame = False