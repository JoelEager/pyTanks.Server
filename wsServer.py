import asyncio
import websockets
import datetime
import random
import json
import numbers
import config

# The websocket server and asyncio functions
#   This takes care of managing the io for the clients and calling the given functions in gameMaster.py at the set rate

# Used to store the info for active clients
class client:
    def __init__(self, clientSocket, type):
        self.socket = clientSocket  # The client's websocket
        self.type = type            # The type of client (valid types defined in config.serverSettings.clientTypes)
        self.outgoing = list()      # The outgoing message queue for this client
        self.incoming = list()      # The incoming message queue for this client

# Each entry is one active client
clients = dict()

# Current number of connected players
playerCount = 0

# Handles logging of events
def logPrint(message, minLevel):
    if config.serverSettings.logLevel >= minLevel:
        print(message)

# Appends a message to the outgoing queues for the indicated client(s)
#   recipient must be a valid int clientID or a type in config.serverSettings.clientTypes
def send(recipient, message):
    if isinstance(recipient, int):
        clients[recipient].outgoing.append(message)
    else:
        for clientID in clients:
            if clients[clientID].type == recipient:
                clients[clientID].outgoing.append(message)

    logPrint("Message added to send queue for " + str(recipient) + ": " + message, 2)

# Appends an error message to a misbehaving client's outing queue
#   If isFatal is True the client is also kicked
def reportClientError(clientID, errorMessage, isFatal):
    if isFatal: errorMessage = "[Fatal Error] " + errorMessage
    else: errorMessage = "[Warning] " + errorMessage

    logPrint("Error sent to client " + str(clientID) + ": " + errorMessage, 1)
    send(clientID, errorMessage)

# Starts the sever and asyncio loop
#    frameCallback:    The function to call every frame
#    updateCallback:   The function to call every client game state update
def runServer(frameCallback, updateCallback):
    # --- Internal websocket server functions: ---

    # Handles incoming messages from a player
    async def playerReceiveTask(clientID):
        global playerCount

        # Used to store a valid command
        class command:
            def __init__(self):
                self.action = message["action"]
                if "arg" in message:
                    self.arg = message["arg"]

        try:
            while clientID in clients:
                message = await clients[clientID].socket.recv()
                logPrint("Got message from " + str(clientID) + ": " + message, 2)

                # Try to parse it as a JSON command
                try:
                    message = json.loads(message)
                except json.decoder.JSONDecodeError:
                    # Message isn't valid JSON
                    raise ValueError("Invalid JSON")

                # All commands must have a valid action
                if message.get("action") not in config.serverSettings.commands.validCommands:
                    raise ValueError("Missing or invalid action")

                # Check for a valid arg if it's required
                if message["action"] == config.serverSettings.commands.turn or \
                        message["action"] == config.serverSettings.commands.fire:
                    if not isinstance(message.get("arg"), numbers.Number):
                        raise ValueError("Missing or invalid arg")

                # Build and append the command obj
                clients[clientID].incoming.append(command())
        except websockets.exceptions.ConnectionClosed:
            # The socket closed
            pass
        except ValueError as e:
            # Bad command so send error to client and disconnect
            reportClientError(clientID, e.args[0], True)

        logPrint("playerReceiveTask for " + str(clientID) + " exited", 1)

    # Registers a client, starts sendTask for it, and watches for incoming messages
    async def clientHandler(websocket, path):
        global playerCount

        # Check the client's connection path and set API type
        if path == config.serverSettings.apiPaths.viewer:
            clientType = config.serverSettings.clientTypes.viewer
        elif path == config.serverSettings.apiPaths.player:
            if playerCount < config.serverSettings.maxPlayers:
                playerCount += 1
                clientType = config.serverSettings.clientTypes.player
            else:
                # Too many players
                logPrint("A player tried to connect but the game is full - connection refused", 1)
                await websocket.send("Server full; please try again later.")
                return  # Returning from this function disconnects the client
        else:
            # Invalid client
            logPrint("A client tried to connect using an invalid API path - connection refused", 1)
            await websocket.send("Invalid API path - Check that your client config is up to date")
            return  # Returning from this function disconnects the client

        # Generate a clientID
        while True:
            if clientType == config.serverSettings.clientTypes.player:
                # If it's a player the id needs to map to a name in the list of tank names
                clientID = random.randint(0, len(config.serverSettings.tankNames) - 1)
            else:
                clientID = random.randint(1000, 9999)

            if clientID not in clients:
                break

        # Add the client to the dictionary of active clients
        clients[clientID] = client(websocket, clientType)

        logPrint("Client (clientID: " + str(clientID) + ", type: " + clients[clientID].type + ") connected", 1)

        # Start a playerReceiveTask if this is a player
        if clientType == config.serverSettings.clientTypes.player:
            asyncio.get_event_loop().create_task(playerReceiveTask(clientID))

        # Send queued messages to the client
        try:
            while clientID in clients:
                if len(clients[clientID].outgoing) != 0:
                    message = clients[clientID].outgoing.pop(0)
                    await clients[clientID].socket.send(message)

                    if message.startswith("[Fatal Error]"):
                        # This is a fatal error message so break out of loop to disconnect the client
                        break
                else:
                    await asyncio.sleep(0.05)
        except websockets.exceptions.ConnectionClosed:
            pass

        # Clean up data for this client
        del clients[clientID]
        if clientType == config.serverSettings.clientTypes.player:
            playerCount -= 1

        logPrint("handler for " + str(clientID) + " exited", 1)
        # (When this function returns the socket dies)

    # Runs frameCallback every frame and aims to hold the given frame rate
    #   Also runs updateCallback at the set rate
    async def frameLoop():
        # For frame rate targeting
        lastFrameTime = datetime.datetime.now()
        baseDelay = 1 / config.serverSettings.framesPerSecond
        delay = baseDelay
        deltas = list()

        # For timing game state updates
        timeSinceLastUpdate = 1 / config.serverSettings.updatesPerSecond

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
            if avgDelta * config.serverSettings.framesPerSecond < 0.95:      # Too fast
                delay += baseDelay * 0.01
            elif avgDelta * config.serverSettings.framesPerSecond > 1.05:    # Too slow
                delay -= baseDelay * 0.01

            if delay < 1 / 250:
                delay = 1 / 250

            # Log FPS if server logging is enabled
            if config.serverSettings.logLevel >= 1:
                frameCount += 1

                if (datetime.datetime.now() - lastFSPLog).total_seconds() >= 5:
                    logPrint("FPS: " + str(frameCount / 5), 1)
                    frameCount = 0
                    lastFSPLog = datetime.datetime.now()

            # Run frameCallback each frame
            frameCallback(frameDelta)

            # Run updateCallback at the rate set in config.py
            timeSinceLastUpdate += frameDelta
            if timeSinceLastUpdate >= 1 / config.serverSettings.updatesPerSecond:
                timeSinceLastUpdate = 0
                updateCallback()

            # Sleep until the next frame
            await asyncio.sleep(delay)      # (If this doesn't sleep then the other tasks can never be completed.)

    # --- Websocket server startup code: ---

    # Configure websocket server logging
    if config.serverSettings.logLevel >= 3:
        import logging
        logger = logging.getLogger("websockets")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        asyncio.get_event_loop().set_debug(True)

    # Start the sever and asyncio loop
    start_server = websockets.serve(clientHandler, config.serverSettings.ip, config.serverSettings.port)
    asyncio.get_event_loop().run_until_complete(start_server)
    logPrint("Server started", 1)
    asyncio.get_event_loop().run_until_complete(frameLoop())