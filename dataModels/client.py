import config
from .tank import tank

class client:
    """
    Used to store the info for an active client
    """
    def __init__(self, clientSocket, clientType):
        self.socket = clientSocket  # The client's websocket
        self.type = clientType      # The type of client (valid types defined in config.server.clientTypes)
        self.outgoing = list()      # The outgoing message queue for this client
        self.incoming = list()      # The incoming message queue for this client

        # Players get a tank
        if clientType == config.server.clientTypes.player:
            self.tank = tank()

    def isPlayer(self):
        """
        :return: A boolean indicating if this client is a player
        """
        return self.type == config.server.clientTypes.player