# Configuration settings for both the game and the server

class gameSettings:
    class mapSize:
        # (0, 0) is the upper left corner with +x going to the right and +y going down
        x = 500                         # In pixels
        y = 500                         # In pixels

    class tankProps:
        speed = 25                      # In pixels per second
        height = 10                     # In pixels
        width = 10                      # In pixels

    shellSpeed = 100                    # In pixels per second

class serverSettings:
    ip = "127.0.0.1"                    # IP address to run the websocket server on
    port = 5678                         # Port to run the websocket server on
    framesPerSecond = 60                # The target frame rate for the frameCallback function
    updatesPerSecond = 10               # How many game state updates should be sent to clients each second
    minPlayers = 4                      # Doesn't start a new game if there's less than this many player clients
    maxPlayers = 20                     # Won't let additional players connect once this number has been reached

    # Level of debugging logging for the websocket server
    logLevel = 1  # 0 for none, 1 for FPS and connect/disconnect, 2 for all server status logs, 3 for all websocket logs

    class apiPaths:
        viewer = "/pyTanksAPI/viewer"   # Path that viewer clients connect on
        player = "/pyTanksAPI/player"   # Path that player clients connect on

    class clientTypes:
        viewer = "viewer"               # A javascript game viewing client
        player = "player"               # A python AI player client

    class tankStatus:
        alive = "alive"                 # The tank is alive and in play
        dead = "dead"                   # The tank is dead (This is also the default state when a new player connects to an in-progress game.)

    tankNames = [                       # User-facing tank names
        "M10 tank destroyer",
        "Cruiser Mk I",
        "Crusader Mk III",
        "Jagdpanzer 38",
        "M3 Stuart",
        "M3 Lee",
        "M7 Priest",
        "M4 Sherman",
        "M18 Hellcat",
        "M22 Locust",
        "M24 Chaffee",
        "M26 Pershing",
        "M36 tank destroyer",
        "Marder III",
        "Matilda II",
        "Panzer I",
        "Panzer V Panther",
        "Panzer IV",
        "Panzer VI Tiger I",
        "Ram medium tank",
        "Sherman Firefly",
        "SU-76",
        "SU-85",
        "SU-100",
        "SU-122",
        "T-37A",
        "T-60",
        "T-72",
        "Type 97 Chi-Ha",
        "Valentine tank Mk III",
        "M48 Patton",
        "M60 Patton",
        "Type 61",
        "M1 Abrams",
        "Chieftain",
        "Challenger 1",
        "Merkava Mk III",
        "M2 Bradley",
        "K2 Black Panther",
        "Leopard 2",
        "Centurion Mk3",
        "Stridsvagn 122",
        "Arjun MBT",
        "K1 88",
        "Panzer 68",
        "Stridsvagn 103",
        "Schneider CA1",
        "Renault FT",
        "Char 2C",
        "Vickers Mk I"
    ]