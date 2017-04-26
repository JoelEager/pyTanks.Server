import asyncio
import websockets
import random

import config
import dataModels
from . import serverData
from .logging import logPrint
from gameLogic.gameClock import gameClock
from gameLogic import gameData

# The pyTanks server backend and asyncio code
#   This takes care of managing the io for the clients and spinning up gameClock.py

# Handles incoming messages from a player
async def __playerReceiveTask(clientID):
    try:
        while clientID in serverData.clients:
            message = await serverData.clients[clientID].socket.recv()
            logPrint("Got message from " + str(clientID) + ": " + message, 4)
            serverData.clients[clientID].incoming.append(dataModels.command(message))
    except websockets.exceptions.ConnectionClosed:
        # The socket closed
        pass
    except ValueError as e:
        # Bad command so send error to client and disconnect
        serverData.reportClientError(clientID, e.args[0], True)

    logPrint("playerReceiveTask for client #" + str(clientID) + " exited", 2)

# Handles sending queued messages to a client
async def __clientSendTask(clientID):
    try:
        while clientID in serverData.clients:
            if len(serverData.clients[clientID].outgoing) != 0:
                message = serverData.clients[clientID].outgoing.pop(0)
                await serverData.clients[clientID].socket.send(message)

                if message.startswith("[Fatal Error]"):
                    # This is a fatal error message so break out of loop to disconnect the client
                    break
            else:
                await asyncio.sleep(0.05)
    except websockets.exceptions.ConnectionClosed:
        pass

    logPrint("clientSendTask for client #" + str(clientID) + " exited", 2)

# Registers a client and starts the io task(s) for it
async def __clientHandler(websocket, path):
    # Check the client's connection path and set API type
    if path == config.server.apiPaths.viewer:
        clientType = config.server.clientTypes.viewer
    elif path == config.server.apiPaths.player:
        if gameData.playerCount < config.server.maxPlayers:
            clientType = config.server.clientTypes.player
        else:
            # Too many players
            logPrint("A player tried to connect but the game is full - connection refused", 1)
            await websocket.send("[Fatal Error] Server full; please try again later.")
            return  # Returning from this function disconnects the client
    else:
        # Invalid client
        logPrint("A client tried to connect using an invalid API path - connection refused", 1)
        await websocket.send("[Fatal Error] Invalid API path - Check that your config.py is up to date")
        return  # Returning from this function disconnects the client

    # Generate a clientID
    while True:
        if clientType == config.server.clientTypes.player:
            # If it's a player the id needs to map to a name in the list of tank names
            clientID = random.randint(0, len(config.server.tankNames) - 1)
        else:
            clientID = random.randint(1000, 9999)

        if clientID not in serverData.clients:
            break

    # Add the client to the dictionary of active clients
    serverData.clients[clientID] = dataModels.client(websocket, clientType)

    logPrint("Client (clientID: " + str(clientID) + ", type: " + serverData.clients[clientID].type + ") connected", 1)

    # Spin up tasks
    if serverData.clients[clientID].isPlayer():
        gameData.playerCount += 1
        asyncio.get_event_loop().create_task(__playerReceiveTask(clientID))

    await __clientSendTask(clientID)
    # (When clientSendTask returns the client's connection has ended or they have been marked for disconnection.)

    # Clean up data for this client
    del serverData.clients[clientID]
    if clientType == config.server.clientTypes.player:
        gameData.playerCount -= 1

    logPrint("handler for client #" + str(clientID) + " exited (connection closed)", 1)
    # (When this function returns the socket dies)

# Starts the sever and asyncio loop
def runServer():
    # Configure websocket server logging
    if config.server.logLevel >= 5:
        import logging
        logger = logging.getLogger("websockets")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        asyncio.get_event_loop().set_debug(True)

    # Start the sever and asyncio loop
    try:
        ipAndPort = config.server.ipAndPort.split(":")
        start_server = websockets.serve(__clientHandler, ipAndPort[0], ipAndPort[1])
        asyncio.get_event_loop().run_until_complete(start_server)
        logPrint("Server started", 1)

        asyncio.get_event_loop().run_until_complete(gameClock())
    except OSError:
        print("Invalid ip and/or port")
    except KeyboardInterrupt:
        # Exit cleanly on ctrl-C
        return