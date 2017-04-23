import datetime
import asyncio

import config
from serverLogic.logging import logPrint
from . import gameData, gameManager

# The asyncio code that maintains a consistent frame rate and runs the on-frame logic

# For timing game state updates
timeSinceLastUpdate = 1 / config.server.updatesPerSecond

# Runs gameManager's and gameData's functions at the rates set in config.py
def onTick(frameDelta):
    global timeSinceLastUpdate

    if not gameData.ongoingGame and gameData.playerCount >= config.server.minPlayers:
        # There's no ongoing game but enough players have joined so start a new game
        gameData.updateClients()  # Ensure that all clients have at least one update with ongoingGame = False
        gameManager.startGame()
        gameData.updateClients()  # Get the new update out ASAP

    if gameData.ongoingGame:
        # There's an ongoing game so run frameCallback
        gameManager.gameTick(frameDelta)

    # Run updateClients at the rate set in config.py
    timeSinceLastUpdate += frameDelta
    if timeSinceLastUpdate >= 1 / config.server.updatesPerSecond:
        timeSinceLastUpdate = 0
        gameData.updateClients()

# Maintains a consistent frame rate as set in config.py
async def gameClock():
    # For frame rate targeting
    lastFrameTime = datetime.datetime.now()
    baseDelay = 1 / config.server.framesPerSecond
    delay = baseDelay
    deltas = list()

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
        if config.server.logLevel >= 1:
            frameCount += 1

            if (datetime.datetime.now() - lastFSPLog).total_seconds() >= 5:
                logPrint("FPS: " + str(frameCount / 5), 3)
                frameCount = 0
                lastFSPLog = datetime.datetime.now()

        # Now do the logic for this frame
        onTick(frameDelta)

        # Sleep until the next frame
        await asyncio.sleep(delay)      # (If this doesn't sleep then the other tasks can never be completed.)