# marching squares algorithm for generating contour data

from heightmap import Heightmap
from chunk import Chunk

class SideHelper:
    def __init__(self, corner1, corner2, x, y):
        self.corner1 = corner1
        self.corner2 = corner2

        self.x = x
        self.y = y


class Cell:

    def __init__(self, tl, tr, br, bl):
        self.sides = [
            SideHelper(bl, tl, 0, None),
            SideHelper(tl, tr, None, 1),
            SideHelper(br, tr, 1, None),
            SideHelper(bl, br, None, 0)
        ]

        self.min_corner_height = min(tl, tr, bl, br)
        self.max_corner_height = max(tl, tr, bl, br)


def parse(heightmap, contour_interval=1, contour_offset=0):

    data = []

    print(heightmap.__dict__)
