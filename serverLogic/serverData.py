from .logging import logPrint

# Holds the server's data structure and the functions for interacting with it

clients = dict()        # Each entry is one active client

# Appends a message to the outgoing queues for the indicated client(s)
#   recipient:  a valid int clientID or a type in config.server.clientTypes
def send(recipients, message):
    if isinstance(recipients, int):
        clients[recipients].outgoing.append(message)
    else:
        for clientID in clients:
            if clients[clientID].type == recipients:
                clients[clientID].outgoing.append(message)

    logPrint("Message added to send queue for " + str(recipients) + ": " + message, 4)

# Appends an error message to a misbehaving client's outing queue
#   If isFatal is True the client is also kicked
def reportClientError(clientID, errorMessage, isFatal):
    if isFatal:
        errorMessage = "[Fatal Error] " + errorMessage
    else:
        errorMessage = "[Warning] " + errorMessage

    clients[clientID].outgoing.append(errorMessage)
    logPrint("Error sent to client " + str(clientID) + ": " + errorMessage, 2)