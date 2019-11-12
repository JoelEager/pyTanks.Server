"""
Manages and updates the game state every frame and sets up new games
"""

from random import randint

import config
from . import collision_detector, gameData
import dataModels
from serverLogic import serverData
from serverLogic.logging import logPrint

def startGame():
    """
    Starts a new game
    """
    gameData.shells = list()
    gameData.walls = list()

    # Create the walls
    for count in range(0, randint(config.game.wall.wallCountBounds[0], config.game.wall.wallCountBounds[1])):
        isValidLocation = False
        aWall = None

        while not isValidLocation:
            aWall = dataModels.wall()
            isValidLocation = True

            # Check for overlap with the other walls
            for otherWall in gameData.walls:
                if collision_detector.has_collided(aWall.toPoly(), otherWall.to_poly(
                        margin=config.game.wall.placementPadding)):
                    isValidLocation = False
                    break

        gameData.walls.append(aWall)

    # Spawn the tanks
    halfWidth = (config.game.map.width / 2) - config.game.tank.width
    halfHeight = (config.game.map.height / 2) - config.game.tank.height
    tanksSpawned = list()

    for clientID in serverData.clients.keys():
        if serverData.clients[clientID].isPlayer():
            tank = serverData.clients[clientID].tank
            tank.spawn()

            isValidLocation = False
            while not isValidLocation:
                tank.x = (config.game.map.width / 2) + randint(-halfWidth, halfWidth)
                tank.y = (config.game.map.height / 2) + randint(-halfHeight, halfHeight)
                isValidLocation = True

                # Check for collisions with the walls
                for wall in gameData.walls:
                    if collision_detector.has_collided(tank.to_poly(), wall.to_poly()):
                        isValidLocation = False
                        break

                # Check for collisions with the other tanks
                for otherTank in tanksSpawned:
                    if collision_detector.has_collided(tank.to_poly(),
                                                       otherTank.to_poly(margin=config.game.tank.spawnPadding)):
                        isValidLocation = False
                        break

            tanksSpawned.append(tank)

    # Start the game
    gameData.ongoingGame = True
    logPrint("New game started with " + str(gameData.playerCount) + " players", 1)

def gameTick(elapsedTime):
    """
    Runs the logic to maintain the game state and applies commands from players
        Called once every frame by gameClock.py
    :param elapsedTime: The time elapsed, in seconds, since the last frame
    """
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
        for point in tankToCheck.to_poly():
            if (point[0] > config.game.map.width or point[0] < 0 or point[1] > config.game.map.height
                    or point[1] < 0):
                didCollide()
                return

        # Check for collisions with other tanks
        for otherTank in otherTanks:
            if collision_detector.has_collided(tankToCheck.to_poly(), otherTank.to_poly(),
                                               max_dist=collision_detector.MaxDistValues.tankTank):
                didCollide()
                return

        # Check for collisions with walls
        for wall in gameData.walls:
            if collision_detector.has_collided(tankToCheck.to_poly(), wall.to_poly()):
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
            if collision_detector.has_collided(gameData.shells[index].to_poly(), wall.to_poly()):
                outOfBoundsShells.insert(0, index)
                break

    for index in outOfBoundsShells:
        del gameData.shells[index]

    # Fill the per-frame lists, execute any commands, and create tanks for new players
    for clientID in serverData.clients.keys():
        if serverData.clients[clientID].isPlayer():
            player = serverData.clients[clientID]

            if player.tank.alive:
                # Execute any commands
                if len(player.incoming) != 0:
                    command = player.incoming.pop()

                    if command.action == config.server.commands.fire:
                        if player.tank.canShoot():
                            player.tank.didShoot()
                            gameData.shells.append(dataModels.shell(clientID, player.tank, command.arg))
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
                if collision_detector.has_collided(tank.to_poly(), shell.to_poly(),
                                                   max_dist=collision_detector.MaxDistValues.tankShell):
                    # Mark tank as dead, give the shooter a kill, and delete the shell
                    tank.alive = False
                    tank.moving = False

                    if shell.shooterId in serverData.clients:
                        serverData.clients[shell.shooterId].tank.kills += 1

                    del gameData.shells[index]
                    break

        # Location checking is only needed for moving tanks
        if tank.moving:
            checkTankLocation(tank)
            otherTanks.append(tank)

    if len(players) <= 1:
        # Game over
        if len(players) == 1:
            # We have a winner!
            serverData.clients[players[0]].tank.wins += 1
            serverData.clients[players[0]].tank.alive = False

        gameData.ongoingGame = False