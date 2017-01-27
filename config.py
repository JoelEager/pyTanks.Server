# This script contains the configuration settings for both the game and the server

class mapSize:
    # (0, 0) is the upper left corner with +x going to the right and +y going down
    x = 500                         # In pixels
    y = 500                         # In pixels

class tankProps:
    speed = 5                       # In pixels per second

class serverSettings:
    ip = "127.0.0.1"                # IP address to run the websocket server on
    port = 5678                     # Port to run the websocket server on
    framesPerSecond = 60            # The target frame rate for the frameCallback function
    updatesPerSecond = 5            # How many game state updates should be sent to clients each second

    # Level of debugging logging for the server
    logLevel = 1  # 0 for none, 1 for FSP and connect/disconnect, 2 for all server status logs, 3 for all websocket logs

    viewerAPIPath = "/viewerAPI"    # Address that viewer clients connect on
    playerAPIPath = "/playerAPI"    # Address that player clients connect on

class clientTypes:
    viewer = "viewer"               # A javascript game viewing client
    player = "player"               # A python AI player client
    invalid = "invalid_API_path"    # An invalid client