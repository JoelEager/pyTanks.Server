import asyncio
import websockets
import datetime

nextId = 0          # The next unused id
logLevel = 0

# Data structures
clients = dict()    # Each entry is one active client
outgoing = dict()   # Each entry is a list of pending outgoing messages for the corresponding client
incoming = dict()   # Each entry is a list of pending incoming messages for the corresponding client

# Handles printing of debug info
def logPrint(message):
    if logLevel >= 1:
        print(message)

# Gets the delta between now and a given datetime in seconds
def timeDelta(aTime):
    diff = datetime.datetime.now() - aTime
    return diff.seconds + (diff.microseconds / 1000000)

# Appends a message to the outgoing queues for all clients
def sendAll(message):
    for id in outgoing:
        outgoing[id].append(message)

    logPrint("Message added to send queue: " + message)

# Sends queued messages to a client
async def sendTask(id, websocket):
    while id in outgoing:
        if len(outgoing[id]) != 0:
            await websocket.send(outgoing[id].pop(0))
        else:
            await asyncio.sleep(0.05)

    logPrint("sendTask for " + str(id) + " exited")

# Registers a client, starts sendTask for it, and watches for incoming messages
async def handler(websocket, path):
    global nextId, clients, outgoing, incoming

    # Register client
    id = nextId
    nextId += 1
    clients[id] = websocket
    outgoing[id] = list()
    incoming[id] = list()
    sendAll("Welcome #" + str(id))

    # Start the sendTask for this socket
    asyncio.get_event_loop().create_task(sendTask(id, websocket))

    # Handles incoming messages from a client
    try:
        while id in clients:
            message = await websocket.recv()
            incoming[id].append(message)

            logPrint("Got message from " + str(id) + ": " + message)
    except websockets.exceptions.ConnectionClosed:
        # The socket closed so remove the client
        clients.pop(id)
        outgoing.pop(id)
        incoming.pop(id)
        sendAll("Bye #" + str(id))

    logPrint("Handler/receiveTask for " + str(id) + " exited")

    # (When this function returns the socket dies)

# Runs the frameCallback every frame and aims to hold the given frameRate
async def mainLoop(frameCallback, framesPerSecond):
    lastFrameTime = datetime.datetime.now()
    baseDelay = 1 / framesPerSecond
    delay = baseDelay
    deltas = list()

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

# Starts the sever and asyncio loop
#    frameCallback:  The function to call every frame
#    frameRate:      The frame rate to target
#    debuggingLevel: 0 for none, 1 for server messages, 2 for all
def main(frameCallback, framesPerSecond, debuggingLevel):
    global logLevel
    logLevel = debuggingLevel

    # Configure websocket server logging
    if logLevel >= 2:
        import logging
        logger = logging.getLogger("websockets")
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())
        asyncio.get_event_loop().set_debug(True)

    # Start the sever and asyncio loop
    start_server = websockets.serve(handler, "127.0.0.1", 5678)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_until_complete(mainLoop(frameCallback, framesPerSecond))