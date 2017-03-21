# pyTanks
 \- A battleground for Python AIs to fight it out.

pyTanks is a project in three modules:
- [Player](https://github.com/JoelEager/pyTanks.Player) - A Python AI that connects to the server and plays the game of tanks.
- [Viewer](https://github.com/JoelEager/pyTanks.Viewer) - A JavaScript/HTML UI for humans to view the ongoing battle.
- Server - A Python server that hosts a top-down, simplistic game of tanks. This takes care of maintaining the game state, handling commands from the players, and sending game state updates to both viewers and players.

Requirements:
- Python 3.5 or newer
- websockets package (pip install websockets)

#### Note: pyTanks is currently in an "alpha" state. Feel free to play around with it and offer feedback but don't expect the code to be feature-complete or fully documented.

## Server
Base functionality is in place but some of the important stuff is still a work in progress.

#### Usage:
```python start.py```

The pyTanks server uses the settings found in config.py to control how the server works. Those values can be changed directly or be overridden by appending one or more of these command line args:
- log=n - Overrides the default logging level. (Replace n with 0 for minimal logging, 1 for FPS and connect/disconnect logs, 2 for all server status logs, or 3 for all websocket logs.)
- ip:port - Overrides the ip and port used to host the server.

#### Licensing note:
The contents of collisionDetector.py are based of off a python implementation of SAT created by Juan Antonio Aldea Armenteros. The original version is available at https://github.com/JuantAldea/Separating-Axis-Theorem/. That code is under the GNU General Public License, but I (Joel Eager) have received written permission to distribute this modified version under the MIT license.

---
(For the other modules see the repos linked at the top of this readme.)