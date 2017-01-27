import wsServer
import gameManager

# This script is responsible for starting up the server with the correct arguments

wsServer.runServer(gameManager.gameLoop)