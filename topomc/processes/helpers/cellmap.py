from enum import Enum

from topomc.common.coordinates import Coordinates


class CellMap:
    def _link_edge(self, cell, edge):
        e = edge
        cell.edges.append(e)
        e.cells.append(cell)

    def __init__(self, heightmap):
        self.cellmap = []

        self.width  = len(heightmap.heightmap[0]) - 1
        self.height = len(heightmap.heightmap)    - 1

        for z in range(self.height):
            cell_row = []
            for x in range(self.width):
                hm = heightmap.heightmap
                
                tl = hm[z]    [x]      # top left
                tr = hm[z]    [x + 1]  # top right
                br = hm[z + 1][x + 1]  # bottom right
                bl = hm[z + 1][x]      # bottom left

                cell = Cell((tl, tr, br, bl), (x, z))

                # left
                if x == 0: self._link_edge(cell, Edge(tl, bl, 0, "y"))
                else:      self._link_edge(cell, cell_row[x - 1].edges[Edge.name.RIGHT.value])
                # top
                if z == 0: self._link_edge(cell, Edge(tl, tr, 0, "x"))
                else:      self._link_edge(cell, self.cellmap[z - 1][x].edges[Edge.name.BOTTOM.value])
                # right
                self._link_edge(cell, Edge(tr, br, cell.coords.x + 1, "y"))
                # bottom
                self._link_edge(cell, Edge(bl, br, cell.coords.y + 1, "x"))

                cell_row.append(cell)

            self.cellmap.append(cell_row)

    def __str__(self):
        return f"Cellmap with width {self.width} and height {self.height}"


class Edge:
    __slots__ = ["corner1", "corner2", "cells", "axis_pos", "type", "contours", "axis"]

    class EdgeName(Enum):
        LEFT = 0
        TOP = 1
        RIGHT = 2
        BOTTOM = 3
    name = EdgeName

    def min_corner(self) -> int: return min(self.corner1, self.corner2)
    def max_corner(self) -> int: return max(self.corner1, self.corner2)

    def __init__(self, corner1: int, corner2: int, axis_pos:int, axis) -> None:
        self.corner1 = corner1
        self.corner2 = corner2
        self.cells   = []
        self.axis_pos = axis_pos
        self.axis = axis

        self.contours = {}
        for possible_height in range(self.min_corner(), self.max_corner() + 1):
            self.contours[possible_height] = {}

    def __repr__(self) -> str:
        return f"{'Vertical' if self.type in self.opposites[0] else 'Horizontal'}\
            Edge ({self.corner1})---({self.corner2}) with coordinates {self.coords!r}"

    @property
    def direction(self) -> int:
        if self.corner1 < self.corner2:
            return 1
        elif self.corner1 > self.corner2:
            return -1
        else:
            return None

    @property
    def difference(self) -> int:
        if self.direction == 1:
            return self.corner2 - self.corner1
        elif self.direction == -1:
            return self.corner1 - self.corner2
        else:
            return 0

class Cell:
    __slots__ = ["corners", "edges", "coords"]

    def __init__(self, corners, coords) -> None:
        self.corners = corners
        self.edges = []

        self.coords = Coordinates(*coords)

    def __repr__(self) -> str:
        return f"Cell {self.corners[0]}==={self.corners[1]}---{self.corners[3]}==={self.corners[2]} at coordinates {self.coords!r}"
