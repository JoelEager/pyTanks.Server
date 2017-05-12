"""
Configuration settings for both the game and the server
"""

class game:
    class map:
        # (0, 0) is the upper left corner with +x going to the right and +y going down
        width = 500                     # In pixels
        height = 500                    # In pixels

    class tank:
        speed = 30                      # In pixels per second
        height = 10                     # In pixels
        width = 10                      # In pixels
        reloadTime = 1.5                # Minimum time to reload the tank's cannon (in seconds)

    class shell:
        speed = 150                     # In pixels per second
        height = 1                      # In pixels
        width = 1                       # In pixels

    class wall:
        shortSideBounds = [15, 30]      # Min and max in pixels
        longSideBounds = [50, 200]      # Min and max in pixels
        placementPadding = 15           # Min padding between walls (including the edge of the map)
        wallCountBounds = [3, 7]        # Min and max number of walls in a game

class server:
    # Both logLevel and ipAndPort can be overridden by command line args so the value here is only the default
    ipAndPort = "localhost:9042"        # The server's IP address and port
    logLevel = 3                        # The amount of server-side logging (See the usage section of the readme)

    framesPerSecond = 60                # The target frame rate for the frameCallback function
    fpsLogRate = 5                      # How many seconds to wait between logging the current FPS
    updatesPerSecond = 10               # How many game state updates should be sent to clients each second
    minPlayers = 4                      # Doesn't start a new game if there's less than this many player clients
    maxPlayers = 15                     # Won't let additional players connect once this number has been reached

    class apiPaths:
        apiVersion = "beta-2"          # Used to make sure the connecting player is up to date

        # Paths for viewer and player clients to connect on:
        player = "/pyTanksAPI/" + apiVersion + "/player"
        viewer = "/pyTanksAPI/viewer"

    class clientTypes:
        viewer = "viewer"               # A javascript game viewing client
        player = "player"               # A python AI player client

    # String names for the commands the player can send
    class commands:
        fire = "Command_Fire"
        turn = "Command_Turn"
        stop = "Command_Stop"
        go = "Command_Go"
        setInfo = "Command_Info"

        infoMaxLen = 200    # The max length for a valid info string
        validCommands = [fire, turn, stop, go, setInfo]

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