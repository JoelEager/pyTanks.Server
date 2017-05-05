# pyTanks
 \- A battleground for Python AIs to fight it out.
 
**See it live at [pytanks.csh.rit.edu](pytanks.csh.rit.edu).**

pyTanks is a project in three modules:
- **Server** - A Python server that hosts a top-down, simplistic game of tanks. This takes care of maintaining the game state, handling commands from the players, and sending game state updates to both viewers and players.
- [Player](https://github.com/JoelEager/pyTanks.Player) - A Python AI that connects to the server and plays the game of tanks.
- [Viewer](https://github.com/JoelEager/pyTanks.Viewer) - A JavaScript/HTML UI for humans to view the ongoing battle.

### Requirements:
- Python 3.5 or newer
- [websockets 3.3](https://github.com/aaugustin/websockets) (`pip install websockets==3.3`)

**Note: pyTanks is currently in beta testing. Please try your hand at making an AI and offer feedback. However, the API and game mechanics are subject to change.**

## Server
### Usage:
```python start.py```

The pyTanks player uses the settings found in `config.py` to control how the client works. Those values can be changed directly or be overridden by appending one or more of these command line args:
- `log=n` - Overrides the default logging level.
- `ip:port` - Overrides the ip and port used to host the server.

Where the log level is one of:
- 0 for no logging
- 1 for connect/disconnect and new game
- 2 for server status and client errors
- 3 for FPS
- 4 for server IO
- 5 for verbose websocket logs

(All log events of a log level equal to or less than the set log level will be printed.)

### Licensing note:
The contents of `collisionDetector.py` are based of off a Python implementation of Separating Axis Theorem created by Juan Antonio Aldea Armenteros. The original version is available [here](https://github.com/JuantAldea/Separating-Axis-Theorem/). That code is under the GNU General Public License, but I (Joel Eager) have received written permission to distribute this modified version under the MIT license.

---
(For the other modules see the repos linked at the top of this readme.)