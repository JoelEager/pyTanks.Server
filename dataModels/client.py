import config
from .tank import tank

# Used to store the info for an active client
class client:
    def __init__(self, clientSocket, clientType):
        self.socket = clientSocket  # The client's websocket
        self.type = clientType      # The type of client (valid types defined in config.server.clientTypes)
        self.outgoing = list()      # The outgoing message queue for this client
        self.incoming = list()      # The incoming message queue for this client

        # Players get a tank
        if clientType == config.server.clientTypes.player:
            self.tank = tank()

    # Returns a boolean indicating if this client is a player
    def isPlayer(self):
        return self.type == config.server.clientTypes.player