from random import randint

import config

class wall:
    """
    Stores the state data for a wall on the map
    """
    def __init__(self):
        """
        Randomly generates a wall using the bounding values in config.py
        """
        # Set lengths for the long and short sides of the wall
        longSide = randint(config.game.wall.longSideBounds[0], config.game.wall.longSideBounds[1])
        shortSide = randint(config.game.wall.shortSideBounds[0], config.game.wall.shortSideBounds[1])

        # Decide if this is going to be a tall or long wall
        if randint(0, 2) == 0:
            self.width, self.height = longSide, shortSide
            self.x = randint(config.game.wall.placementPadding, config.game.map.width -
                             config.game.wall.placementPadding - config.game.wall.longSideBounds[0])
            self.y = randint(config.game.wall.placementPadding, config.game.map.height -
                             config.game.wall.placementPadding - config.game.wall.shortSideBounds[0])
        else:
            self.height, self.width = longSide, shortSide
            self.y = randint(config.game.wall.placementPadding, config.game.map.height -
                             config.game.wall.placementPadding - config.game.wall.longSideBounds[0])
            self.x = randint(config.game.wall.placementPadding, config.game.map.width -
                             config.game.wall.placementPadding - config.game.wall.shortSideBounds[0])

        # Check to make sure the wall doesn't go too far
        if self.x + self.width > config.game.map.width - config.game.wall.placementPadding:
            self.width = config.game.map.width - config.game.wall.placementPadding - self.x
        elif self.y + self.height > config.game.map.height - config.game.wall.placementPadding:
            self.height = config.game.map.height - config.game.wall.placementPadding - self.y

        # Correct x and y to be the center of the wall instead of top-left corner
        self.x += self.width / 2
        self.y += self.height / 2

    def toPoly(self, margin=0):
        """
        :param margin: If set the polygon will have a padding of margin pixels in every direction
        :return: The wall's polygon as a list of points as tuples
        """
        halfWidth = (self.width / 2) + margin
        halfHeight = (self.height / 2) + margin
        return [(self.x - halfWidth, self.y - halfHeight),
                (self.x - halfWidth, self.y + halfHeight),
                (self.x + halfWidth, self.y - halfHeight),
                (self.x + halfWidth, self.y + halfHeight)]