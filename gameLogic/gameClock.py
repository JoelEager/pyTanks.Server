"""
The asyncio code that maintains a consistent frame rate and runs the on-frame logic
"""

import datetime
import asyncio

import config
from serverLogic.logging import logPrint, round
from . import gameData, gameManager

# For timing game state updates
__timeSinceLastUpdate = 1 / config.server.updatesPerSecond

def __onTick(frameDelta):
    """
    Runs gameManager's and gameData's functions at the rates set in config.py
    :param frameDelta: The time elapsed, in seconds, since the last frame
    """
    global __timeSinceLastUpdate

    if not gameData.ongoingGame and gameData.playerCount >= config.server.minPlayers:
        # There's no ongoing game but enough players have joined so start a new game
        gameData.updateClients()  # Ensure that all clients have at least one update with ongoingGame = False
        gameManager.startGame()
        gameData.updateClients()  # Get the new update out ASAP

    if gameData.ongoingGame:
        # There's an ongoing game so run frameCallback
        gameManager.gameTick(frameDelta)

    # Run updateClients at the rate set in config.py
    __timeSinceLastUpdate += frameDelta
    if __timeSinceLastUpdate >= 1 / config.server.updatesPerSecond:
        __timeSinceLastUpdate = 0
        gameData.updateClients()

async def gameClock():
    """
    Maintains a consistent frame rate as set in config.py and calls onTick() every frame
    """
    # For frame rate targeting
    lastFrameTime = datetime.datetime.now()
    baseDelay = 1 / config.server.framesPerSecond
    delay = baseDelay
    deltas = list()
    minFPS = config.server.framesPerSecond

    # For calculating the FPS for logging
    lastFSPLog = datetime.datetime.now()
    frameCount = 0

    while True:
        # Calculate the time passed in seconds and adds it to the list of deltas
        frameDelta = (datetime.datetime.now() - lastFrameTime).total_seconds()
        lastFrameTime = datetime.datetime.now()
        deltas.append(frameDelta)
        if len(deltas) > 15:
            del deltas[0]

        # Adjust delay to try to keep the actual frame rate within 5% of the target
        avgDelta = sum(deltas) / float(len(deltas))
        if avgDelta * config.server.framesPerSecond < 0.95:      # Too fast
            delay += baseDelay * 0.01
        elif avgDelta * config.server.framesPerSecond > 1.05:    # Too slow
            delay -= baseDelay * 0.01

        if delay < 1 / 250:
            delay = 1 / 250

        # Log FPS if FPS logging is enabled
        if avgDelta != 0:
            if 1 / avgDelta < minFPS:
                minFPS = 1 / avgDelta

        if config.server.logLevel >= 1:
            frameCount += 1

            if (datetime.datetime.now() - lastFSPLog).total_seconds() >= config.server.fpsLogRate:
                logPrint("FPS: avg=" + str(frameCount / config.server.fpsLogRate) + ", min=" +
                         str(round(minFPS, 1)), 3)
                frameCount = 0
                minFPS = config.server.framesPerSecond
                lastFSPLog = datetime.datetime.now()

        # Now do the logic for this frame
        __onTick(frameDelta)

        # Sleep until the next frame
        await asyncio.sleep(delay)      # (If this doesn't sleep then the other tasks can never be completed.)