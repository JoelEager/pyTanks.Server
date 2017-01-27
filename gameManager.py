import wsServer
import datetime

debuggingLevel = 1  # 0 for none, 1 for server messages, 2 for all

lastLogTime = datetime.datetime.now()

def gameLoop():
    global lastLogTime

    # Print the messages received from the clients
    for id in wsServer.incoming:
        while len(wsServer.incoming[id]) != 0:
            print(str(id) + ": " + wsServer.incoming[id].pop())

    # Send an update to the clients every 5 seconds
    if wsServer.timeDelta(lastLogTime) >= 5:
        message = "Number of clients: " + str(len(wsServer.clients))
        lastLogTime = datetime.datetime.now()
        wsServer.sendAll(message)

wsServer.main(gameLoop, 60, debuggingLevel)