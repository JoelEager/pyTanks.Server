# Configuration settings for both the game and the server

class game:
    class map:
        # (0, 0) is the upper left corner with +x going to the right and +y going down
        width = 500                     # In pixels
        height = 500                    # In pixels

    class tank:
        speed = 25                      # In pixels per second
        height = 10                     # In pixels
        width = 10                      # In pixels
        reloadTime = 2                  # Minimum time to reload the tank's cannon (in seconds)

    class shell:
        speed = 100                     # In pixels per second
        height = 1                      # In pixels
        width = 1                       # In pixels

    class wall:
        shortSideBounds = [15, 50]      # Min and max in pixels
        longSideBounds = [50, 100]      # Min and max in pixels
        placementPadding = 15           # Min padding between a wall and the map bounds

class server:
    # Both logLevel and ipAndPort can be overridden by command line args so the value here is only the default
    ipAndPort = "localhost:9042"        # The server's IP address and port
    logLevel = 1                        # Level of debugging logging for the websocket server
    # (0 for minimal, 1 for FPS and connect/disconnect, 2 for all server status logs, 3 for all websocket logs)

    framesPerSecond = 60                # The target frame rate for the frameCallback function
    updatesPerSecond = 10               # How many game state updates should be sent to clients each second
    minPlayers = 4                      # Doesn't start a new game if there's less than this many player clients
    maxPlayers = 20                     # Won't let additional players connect once this number has been reached

    class apiPaths:
        viewer = "/pyTanksAPI/viewer"   # Path that viewer clients connect on
        player = "/pyTanksAPI/player"   # Path that player clients connect on

    class clientTypes:
        viewer = "viewer"               # A javascript game viewing client
        player = "player"               # A python AI player client

    class tankStatus:
        alive = "alive"                 # The tank is alive and in play
        dead = "dead"                   # The tank is dead (This is also the default state when a new player connects
                                        #   to an in-progress game.)

    # String names for the commands the player can send
    class commands:
        fire = "Command_Fire"
        turn = "Command_Turn"
        stop = "Command_Stop"
        go = "Command_Go"

        validCommands = [fire, turn, stop, go]

    # User-facing tank names
    tankNames = [
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