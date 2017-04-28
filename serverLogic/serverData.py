"""
Holds the server's data structure and the functions for interacting with it
"""

from .logging import logPrint

clients = dict()        # Each entry is one active client

def send(recipients, message):
    """
    Appends a message to the outgoing queues for the indicated client(s)
    :param recipients: A valid int clientID or a type in config.server.clientTypes
    """
    if isinstance(recipients, int):
        clients[recipients].outgoing.append(message)
    else:
        for clientID in clients:
            if clients[clientID].type == recipients:
                clients[clientID].outgoing.append(message)

    logPrint("Message added to send queue for " + str(recipients) + ": " + message, 4)

def reportClientError(clientID, errorMessage, isFatal):
    """
    Appends an error message to a misbehaving client's outing queue
    :param isFatal: If this is True the client is also kicked
    """
    if isFatal:
        errorMessage = "[Fatal Error] " + errorMessage
    else:
        errorMessage = "[Warning] " + errorMessage

    clients[clientID].outgoing.append(errorMessage)
    logPrint("Error sent to client " + str(clientID) + ": " + errorMessage, 2)