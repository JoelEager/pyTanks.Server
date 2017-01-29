import asyncio
import websockets
import datetime
import random
import config

# This script is the websocket server and asyncio loop
#   It takes care of managing the io for the clients and calling the frameCallback function once every frame

# Used to store the info for one active client
class client:
    def __init__(self, clientSocket, path):
        self.socket = clientSocket  # The client's websocket
        self.outgoing = list()      # The outgoing message queue for this client
        self.incoming = list()      # The incoming message queue for this client

        # Set the client's type
        if path == config.serverSettings.viewerAPIPath:
            self.type = config.clientTypes.viewer
        elif path == config.serverSettings.playerAPIPath:
            self.type = config.clientTypes.player
        else:
            self.type = config.clientTypes.invalid

# Each entry is one active client
clients = dict()

# Appends a message to the outgoing queues for all clients
def sendAll(message):
    for clientID in clients:
        clients[clientID].outgoing.append(message)

    if config.serverSettings.logLevel >= 2:
        print("Message added to send queue: " + message)

# Starts the sever and asyncio loop
#    frameCallback:    The function to call every frame
#    framesPerSecond:  The number of frames per second to target
def runServer(frameCallback):
    # --- Internal server functions: ---

    # Handles printing of debug info
    def logPrint(message, minLevel):
        if config.serverSettings.logLevel >= minLevel:
            print(message)

    # Gets the delta between now and a given datetime in seconds
    def timeDelta(aTime):
        diff = datetime.datetime.now() - aTime
        return diff.seconds + (diff.microseconds / 1000000)

    # Sends queued messages to a client
    async def sendTask(clientID):
        while clientID in clients:
            if len(clients[clientID].outgoing) != 0:
                await clients[clientID].socket.send(clients[clientID].outgoing.pop(0))
            else:
                await asyncio.sleep(0.05)

        logPrint("sendTask for " + str(clientID) + " exited", 1)

    # Registers a client, starts sendTask for it, and watches for incoming messages
    async def clientHandler(websocket, path):
        # Generate a clientID
        while True:
            clientID = random.randint(1000, 9999)

            if clientID not in clients:
                break

        # Add the client to the dictionary of active clients
        clients[clientID] = client(websocket, path)

        logPrint("Client (clientID: " + str(clientID) + ", type: " + clients[clientID].type + ") connected at " + path, 1)

        # Start the sendTask for this socket
        asyncio.get_event_loop().create_task(sendTask(clientID))

        # Handles incoming messages from a client
        try:
            while clientID in clients:
                message = await websocket.recv()
                clients[clientID].incoming.append(message)

                logPrint("Got message from " + str(clientID) + ": " + message, 2)
        except websockets.exceptions.ConnectionClosed:
            # The socket closed so remove the client
            clients.pop(clientID)

        logPrint("Handler/receiveTask for " + str(clientID) + " exited", 1)

        # (When this function returns the socket dies)

    # Runs the frameCallback every frame and aims to hold the given frame rate
    async def frameLoop():
        # For frame rate targeting
        lastFrameTime = datetime.datetime.now()
        baseDelay = 1 / config.serverSettings.framesPerSecond
        delay = baseDelay
        deltas = list()

        # For calculating the FPS for logging
        lastFSPLog = datetime.datetime.now()
        frameCount = 0

        while True:
            # Calculate the time passed in seconds and adds it to the list of deltas
            frameDelta = timeDelta(lastFrameTime)
            lastFrameTime = datetime.datetime.now()
            deltas.append(frameDelta)
            if len(deltas) > 15:
                deltas.pop(0)

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

                if timeDelta(lastFSPLog) >= 5:
                    print("FPS: " + str(frameCount / 5))
                    frameCount = 0
                    lastFSPLog = datetime.datetime.now()

            # Run the callback
            frameCallback(frameDelta)

            # Sleep until the next frame
            await asyncio.sleep(delay)      # (If this doesn't sleep then the other tasks can never be completed.)

    # --- Server startup code: ---

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
    print("Server started")
    asyncio.get_event_loop().run_until_complete(frameLoop())