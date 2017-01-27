import asyncio
import websockets
import datetime
import random

# Level of debugging logging
logLevel = 0   # 0 for none, 1 for server messages, 2 for all

# Used to store the info for one active client
class client:
    def __init__(self, clientSocket, path):
        self.socket = clientSocket  # The client's websocket
        self.type = "viewer"        # The client type
        self.outgoing = list()      # The outgoing message queue for this client
        self.incoming = list()      # The incoming message queue for this client

# Each entry is one active client
clients = dict()

# Appends a message to the outgoing queues for all clients
def sendAll(message):
    for clientID in clients:
        clients[clientID].outgoing.append(message)

    if logLevel >= 1:
        print("Message added to send queue: " + message)

# Starts the sever and asyncio loop
#    frameCallback:    The function to call every frame
#    framesPerSecond:  The number of frames per second to target
def runServer(frameCallback, framesPerSecond):
    # --- Internal server functions: ---

    # Handles printing of debug info
    def logPrint(message):
        if logLevel >= 1:
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

        logPrint("sendTask for " + str(clientID) + " exited")

    # Registers a client, starts sendTask for it, and watches for incoming messages
    async def clientHandler(websocket, path):
        # Generate a clientID
        while True:
            clientID = random.randint(1000, 9999)

            if clientID not in clients:
                break

        # Add the client to the dictionary of active clients
        clients[clientID] = client(websocket, path)

        logPrint("Client with clientID " + str(clientID) + " connected at " + path)
        sendAll("Welcome #" + str(clientID))

        # Start the sendTask for this socket
        asyncio.get_event_loop().create_task(sendTask(clientID))

        # Handles incoming messages from a client
        try:
            while clientID in clients:
                message = await websocket.recv()
                clients[clientID].incoming.append(message)

                logPrint("Got message from " + str(clientID) + ": " + message)
        except websockets.exceptions.ConnectionClosed:
            # The socket closed so remove the client
            clients.pop(clientID)
            sendAll("Bye #" + str(clientID))

        logPrint("Handler/receiveTask for " + str(clientID) + " exited")

        # (When this function returns the socket dies)

    # Runs the frameCallback every frame and aims to hold the given frame rate
    async def frameLoop():
        # For frame rate targeting
        lastFrameTime = datetime.datetime.now()
        baseDelay = 1 / framesPerSecond
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
            if avgDelta * framesPerSecond < 0.95:      # Too fast
                delay += baseDelay * 0.01
            elif avgDelta * framesPerSecond > 1.05:    # Too slow
                delay -= baseDelay * 0.01

            if delay < 1 / 250:
                delay = 1 / 250

            # Log FPS if server logging is enabled
            if logLevel >= 1:
                frameCount += 1

                if timeDelta(lastFSPLog) >= 5:
                    print("FPS: " + str(frameCount / 5))
                    frameCount = 0
                    lastFSPLog = datetime.datetime.now()

            # Run the callback
            frameCallback()

            # Sleep until the next frame
            await asyncio.sleep(delay)      # (If this doesn't sleep then the other tasks can never be completed.)

    # --- Server startup code: ---

    # Configure websocket server logging
    if logLevel >= 2:
        import logging
        logger = logging.getLogger("websockets")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        asyncio.get_event_loop().set_debug(True)

    # Start the sever and asyncio loop
    start_server = websockets.serve(clientHandler, "127.0.0.1", 5678)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_until_complete(frameLoop())