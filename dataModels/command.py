import json
import numbers
import datetime

import config

# Used to store an incoming player command
class command:
    # Called with a raw message string from a client
    #   raises a ValueError if the message isn't a valid command
    def __init__(self, message):
        # Try to parse it as a JSON command
        try:
            message = json.loads(message)
        except json.decoder.JSONDecodeError:
            # Message isn't valid JSON
            raise ValueError("Invalid JSON")

        # All commands must have a valid action
        if message.get("action") not in config.server.commands.validCommands:
            raise ValueError("Missing or invalid action")

        self.action = message["action"]

        # Check for a valid arg if it's required
        if self.action == config.server.commands.turn or self.action == config.server.commands.fire:
            if not isinstance(message.get("arg"), numbers.Number):
                raise ValueError("Missing or invalid arg")

            self.arg = message["arg"]