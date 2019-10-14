from collections import deque, namedtuple

class Point(namedtuple('Point', ['x', 'y'])):

    def __add__(self,  other):
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

class SnakeDirection(object):

    NORTH = Point(0, -1)
    EAST = Point(1, 0)
    SOUTH = Point(0, 1)
    WEST = Point(-1, 0)

class Snake(object):
    def __init__(self, start_coord=None, length=1):
        self.body = deque([Point(start_coord.x, start_coord.y + i) for i in range(length)])
        self.directtion = SnakeDirection.NORTH

    def __str__(self):
        sep = "\n"
        return "length: " + str(self.length) + "\n" + sep.join(["x:" + str(p.x) + ", y:" + str(p.y) for p in self.body])

    @property
    def head(self):
        return self.body[0]

    @property
    def length(self):
        return len(self.body)

    def move(self, direction):
        """ Move the snake with a given direction """
        self.body.appendleft(self.head + direction)

    def peekDirection(self, direction):
        """ Get the point the snake will move to at its next step. """
        return self.head + direction

import numpy as np
from itertools import islice
if __name__ == "__main__":
    s = Snake(Point(2, 4))
    p = Point(1, 40)
    a = deque([Point(2, 4), Point(1, 4), Point(4, 4), Point(2, 4)])
    print(Point(2,4) in islice(a, 1, None))
    