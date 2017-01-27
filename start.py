import wsServer
import gameManager

wsServer.runServer(gameManager.gameLoop, 60)