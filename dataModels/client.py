from datetime import datetime

import config
from .tank import tank

class client:
    """
    Used to store the info for an active client
    """
    def __init__(self, clientSocket, clientType):
        self.socket = clientSocket          # The client's websocket
        self.type = clientType              # The type of client (valid types defined in config.server.clientTypes)
        self.outgoing = list()              # The outgoing message queue for this client
        self.incoming = list()              # The incoming message queue for this client
        self.lastReceived = datetime.now()  # The last time a message was received from this client

        # Players get a tank
        if clientType == config.server.clientTypes.player:
            self.tank = tank()

    def isPlayer(self):
        """
        :return: A boolean indicating if this client is a player
        """
        return self.type == config.server.clientTypes.player

    def receivedMsg(self):
        """
        Called when a message is received to update lastReceived
        """
        self.lastReceived = datetime.now()

    def hasTimedOut(self):
        """
        :return: A boolean indicating if this client hasn't sent a message within the timeout duration
        """
        return (datetime.now() - self.lastReceived).total_seconds() > config.server.timeout