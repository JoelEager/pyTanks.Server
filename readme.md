# pyTanks
 \- A battleground for Python AIs to fight it out.
 
**See it live at [pytanks.csh.rit.edu](http://pytanks.csh.rit.edu).**

pyTanks is a project in three modules:
- **Server** - A Python server that hosts a top-down, simplistic game of tanks. This takes care of 
maintaining the game state, handling commands from the players, and sending game state updates to both 
viewers and players.
- [Player](https://github.com/JoelEager/pyTanks.Player) - A Python AI that connects to the server and 
plays the game of tanks.
- [Viewer](https://github.com/JoelEager/pyTanks.Viewer) - A JavaScript/HTML UI for humans to view the 
ongoing battle.

### Requirements
- Python 3.5 or newer
- [websockets 3.3](https://github.com/aaugustin/websockets) (`pip3 install websockets==3.3`)

## Server
### Usage
```python3 start.py```

The pyTanks player uses the settings found in `config.py` to control how the client works. Those values 
can be changed directly or be overridden by appending one or more of these command line args:
- `log=n` - Overrides the default logging level.
- `ip:port` - Overrides the ip and port used to host the server.

Where the log level is one of:
- 0 for no logging
- 1 for connect/disconnect and new game
- 2 for server status and client errors
- 3 for FPS and client counts
- 4 for server IO
- 5 for verbose websocket logs

(All log events of a log level equal to or less than the set log level will be printed.)

### Project structure
The pyTanks server is built around ansycio tasks with a main game logic task, an incoming messages task 
for each connected player, and an outgoing messages task for each connected client of either kind.

Here's a quick overview of how the code is laid out:
- `dataModels` - Contains the classes used for storing and organizing game and server state.
- `gameLogic` - Contains all the logic for running the game (game clock, per-frame logic, game state
 update generation, and so on).
- `serverLogic` - Contains all the logic for running the server (websocket io tasks, client management, 
logging, and so on).
- `config.py` - Stores the settings and constants used by the server.
- `start.py` - A startup script which handles the command line args and checks the requirements. 

The files, functions, and classes contain pretty thorough documentation on the design and structure 
of the server.

### Licensing note
The contents of `collisionDetector.py` are based of off a Python implementation of Separating Axis 
Theorem created by Juan Antonio Aldea Armenteros. The original version is available 
[here](https://github.com/JuantAldea/Separating-Axis-Theorem/). That code is under the GNU General 
Public License, but I (Joel Eager) have received written permission to distribute this modified 
version under the MIT license.

---
(For the other modules see the repos linked at the top of this readme.)