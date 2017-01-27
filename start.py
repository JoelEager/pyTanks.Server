import wsServer
import gameManager

wsServer.logLevel = 1   # 0 for none, 1 for server messages, 2 for all
wsServer.runServer(gameManager.gameLoop, 60)