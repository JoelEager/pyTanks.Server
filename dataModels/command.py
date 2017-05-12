import json
import numbers
import html

import config

class command:
    """
    Used to store an incoming player command
    """
    def __init__(self, message):
        """
        Called with a raw message string from a client
        :raise: ValueError if the message isn't a valid command
        """
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
        elif self.action == config.server.commands.setInfo:
            self.arg = str(message.get("arg"))

            if len(self.arg) > config.server.commands.infoMaxLen:
                raise ValueError("Info string is longer than " + str(config.server.commands.infoMaxLen) + " characters")

            self.arg = html.escape(self.arg)
            self.arg = self.arg.replace("\n", " <br /> ")

            # Parse urls
            start = self.arg.find("http")
            while start != -1:
                end = self.arg.find(" ", start)
                if end == -1:
                    end = len(self.arg)

                if self.arg[start:start + 7] == "http://" or self.arg[start:start + 8] == "https://":
                    url = self.arg[start:end]
                    aTag = "<a href='" + url + "' target='_blank'>" + url + "</a>"
                    self.arg = self.arg[:start] + aTag + self.arg[end:]
                    end += len(aTag) - len(url)

                start = self.arg.find("http", end)
        else:
            if "arg" in message:
                raise ValueError("Unexpected arg")