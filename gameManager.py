import wsServer
import datetime

lastLogTime = datetime.datetime.now()

def gameLoop():
    global lastLogTime

    # Print the messages received from the clients
    for clientID in wsServer.clients:
        while len(wsServer.clients[clientID].incoming) != 0:
            print(str(clientID) + ": " + wsServer.clients[clientID].incoming.pop())

    # Send an update to the clients every 5 seconds
    timeDelta = datetime.datetime.now() - lastLogTime
    timeDelta = timeDelta.seconds + (timeDelta.microseconds / 1000000)
    if timeDelta >= 5:
        message = "Number of clients: " + str(len(wsServer.clients))
        lastLogTime = datetime.datetime.now()
        wsServer.sendAll(message)