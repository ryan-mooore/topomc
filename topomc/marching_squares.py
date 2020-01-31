# marching squares algorithm for generating contour data

from heightmap import Heightmap
from chunk import Chunk

class Side:
    def __init__(self, corner1, corner2, x, y):
        self.corner1 = corner1
        self.corner2 = corner2

        self.x = x
        self.y = y


class Cell:

    def __init__(self, nodes):
        tl, tr, br, bl = nodes
        
        self.sides = [
            SideHelper(bl, tl, 0, None),
            SideHelper(tl, tr, None, 1),
            SideHelper(br, tr, 1, None),
            SideHelper(bl, br, None, 0)
        ]

        self.min_node = min(tl, tr, bl, br)
        self.max_node = max(tl, tr, bl, br)


def parse(heightmap, contour_interval=1, contour_offset=0):

    data = []

    for height_plane in range(heightmap.min_height, heightmap.max_height + 1):
        hmap = heightmap.map
        for y in range (len(hmap) - 1):
            for x in range(len(hmap[y]) - 1):
                cell = Cell([
                    hmap[y]    [x]    ,
                    hmap[y]    [x + 1],
                    hmap[y + 1][x + 1],
                    hmap[y + 1][x]    ,
                ])
                
                if cell.min_node <= height_plane and cell.max_node > height_plane:
                    


