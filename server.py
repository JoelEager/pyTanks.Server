import asyncio
import websockets
import datetime

# Debugging logging level
logLevel = 0   # 0 for none, 1 for server messages, 2 for all

# Websocket server logging
if logLevel >= 2:
    import logging
    logger = logging.getLogger("websockets")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    asyncio.get_event_loop().set_debug(True)

# Handles printing of debug info
def logPrint(message):
    if logLevel >= 1:
        print(message)

# Data structures
nextId = 0          # The next unused id
clients = dict()    # Each entry is one active client
outgoing = dict()   # Each entry is a list of pending outgoing messages for the corresponding client
incoming = dict()   # Each entry is a list of pending incoming messages for the corresponding client

# Appends a message to the outgoing queues for all clients
def sendAll(message):
    for id in outgoing:
        outgoing[id].append(message)

    logPrint("Message added to send queue: " + message)

# Handle a client
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

# Sends queued messages to a client
async def sendTask(id, websocket):
    while id in outgoing:
        if len(outgoing[id]) != 0:
            await websocket.send(outgoing[id].pop(0))
        else:
            await asyncio.sleep(0.05)

    logPrint("sendTask for " + str(id) + " exited")

# Runs the logic for sending and receiving messages
#   - game logic could go here
async def mainLoop():
    startTime = datetime.datetime.now()
    frameCount = 0

    while True:
        # Print the messages received from the clients
        for id in incoming:
            while len(incoming[id]) != 0:
                print(str(id) + ": " + incoming[id].pop())

        frameCount += 1
        timeDelta = datetime.datetime.now() - startTime

        # Send an update to the clients every 5 seconds
        if timeDelta.seconds >= 5:
            message = "Time passed: " + str(timeDelta.seconds) + "." + str(timeDelta.microseconds) + " seconds;" \
                      " FPS: " + str(frameCount / (timeDelta.seconds + (timeDelta.microseconds / 100000))) + "; " \
                      " Number of clients: " + str(len(clients))
            startTime = datetime.datetime.now()
            frameCount = 0
            sendAll(message)

        await asyncio.sleep(1/60)      # If this doesn't sleep then the other tasks can never be completed

start_server = websockets.serve(handler, "127.0.0.1", 5678)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_until_complete(mainLoop())