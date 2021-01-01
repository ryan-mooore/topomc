# marching squares algorithm for generating contour data

from typing import List, Tuple
from topomc.common.logger import Logger
from enum import Enum
import logging


class Edge:
    __slots__ = ["corner1", "corner2", "cells", "coords", "type", "contours", "orientation"]

    class EdgeName(Enum):
        LEFT = 0
        TOP = 1
        RIGHT = 2
        BOTTOM = 3
    name = EdgeName

    def min_corner(self) -> int: return min(self.corner1, self.corner2)
    def max_corner(self) -> int: return max(self.corner1, self.corner2)

    def __init__(self, corner1: int, corner2: int, x: int, y: int, orientation) -> None:
        self.corner1 = corner1
        self.corner2 = corner2
        self.cells   = []
        self.coords  = Coordinates(x, y)
        self.orientation = orientation

        self.contours = {}
        for possible_height in range(self.min_corner(), self.max_corner() + 1):
            self.contours[possible_height] = None

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

    def __init__(self, corners: List[int], coords: Tuple[int]) -> None:
        self.corners = corners
        self.edges = []

        self.coords = Coordinates(*coords)

    def __repr__(self) -> str:
        return f"Cell {self.corners[0]}==={self.corners[1]}---\
                      {self.corners[2]}==={self.corners[3]} at coordinates {self.coords!r}"

class Isoline:
    def __init__(self) -> None:
        self.contour:List[Tuple[float]] = []
        self.direction = 0
        self.closed = False
    
    def __repr__(self) -> str:
        return "---".join([repr(cell[1]) for cell in self.contour])

class Coordinates:
    __slots__ = ["x", "y"]

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    
    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Coordinates):
            return NotImplemented

        return self.x == other.x and self.y == other.y

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
                if x == 0: self._link_edge(cell, Edge(bl, tl, 0, None, True))
                else:      self._link_edge(cell, cell_row[x - 1].edges[Edge.name.RIGHT.value])
                # top
                if z == 0: self._link_edge(cell, Edge(tl, tr, None, 1, False))
                else:      self._link_edge(cell, self.cellmap[z - 1][x].edges[Edge.name.BOTTOM.value])
                # right
                self._link_edge(cell, Edge(br, tr, 1, None, True))
                # bottom
                self._link_edge(cell, Edge(bl, br, None, 0, False))

                cell_row.append(cell)

            self.cellmap.append(cell_row)

    def __str__(self):
        return f"Cellmap with width {self.width} and height {self.height}"

class TopoMap:
    def __init__(self, cellmap):
        self.isolines = []

        self.width = cellmap.width
        self.height = cellmap.height

        def traverse(cell: Cell, edge: Edge) -> Cell:
            cells = [*edge.cells]
            cells.remove(cell)
            return cells[0]

        def create_point_coords(edge: Edge, point: float) -> Coordinates:
            coords = Coordinates(edge.coords.x, edge.coords.y)
            if coords.x == None: coords.x = point
            if coords.y == None: coords.y = point
            return coords

        def has_self_closed(isoline, custom_check: Tuple=None):
            if isoline.closed:
                if isoline.contour[0] == (custom_check if custom_check else isoline.contour[-1]):
                    return True
                else:
                    return False
        
        def get_local_coords(height, edge):
            point = (height - edge.min_corner() + 1) / (edge.difference + 1)
            if edge.direction == -1: point = 1 - point
            return create_point_coords(edge, point)

        def height_within_difference(height, edge):
            return edge.min_corner() <= height < edge.max_corner() # a contour starts at this edge at this height

        def trace_from_here(cell, edge, height, closed=False) -> Isoline:
            if height_within_difference(height, edge):
                isoline = Isoline() # create contour
                if closed:
                    isoline.closed = True # this contour will not touch the edge; therefore must be closed
                else:
                    edge.contours[height] = isoline
                    isoline.contour.append((get_local_coords(height, edge), cell.coords))

                # trace
                while True:
                    edges = [*cell.edges]
                    edges.remove(edge)
                    edges.sort(key=lambda e: e.orientation == edge.orientation) # sort by adjacent first, then opposite (to avoid crossover)
                    for edge in edges:
                        if height_within_difference(height, edge):
                            if edge.contours[height]: # if a contour at the same height exists
                                if isoline.closed and edge.contours[height] == isoline: # we only need to consider this edge if the isoline needs to be closed and is the same one we are tracing
                                        coords = get_local_coords(height, edge) # create the coordinates as if we have traced to it
                                        if has_self_closed(isoline, custom_check=(coords, cell.coords)): # do they match the start of the loop?
                                            isoline.contour.append((coords, cell.coords)) # if yes we have closed the contour and we are done
                                            return isoline
                                            # if no then we have reached the same contour but haven't looped back to the start yet. Try another edge
                                continue # if the contour does not need to be closed we don't care. we can't go to this edge. Try another edge
                            else:
                                pass
                                # no existing contour, easy trace to this edge

                            edge.contours[height] = isoline # mark the edge as visited
                            isoline.contour.append((get_local_coords(height, edge), cell.coords)) # and add the coordinates to the contour

                            if len(edge.cells) == 1: # if the boundary has been hit the contour is complete
                                return isoline
                            else:
                                cell = traverse(cell, edge) # otherwise trace again!
                                break # go to next cell
                    else:
                        # this should never occur. if it does it means that there were no edges to trace to and the contour has to end prematurely
                        logging.critical(f"Routing Error at {cell.coords}")
                        break # do not draw the contour
        
        def start_traces(cell: Cell, edgename: Edge.name) -> None:
            edge = cell.edges[edgename] 
            for height in range(edge.min_corner(), edge.max_corner() + 1): # start a trace for every height in the cell
                if not edge.contours[height]: # check that a contour hasn't already been traced to here 
                    isoline = trace_from_here(cell, cell.edges[edgename], height) #  and start the trace
                    if isoline: # check that the contour is actually a line
                        self.isolines.append(isoline) # add the contour

        # find all open contours (open contours will always touch the edge)
        Logger.log(logging.info, "Tracing open contours...", sub=1)
        for cell in cellmap.cellmap[0]: start_traces(cell, Edge.name.TOP.value)
        for row in cellmap.cellmap: start_traces(row[len(row) - 1], Edge.name.RIGHT.value)
        for cell in cellmap.cellmap[len(cellmap.cellmap) - 1]: start_traces(cell, Edge.name.BOTTOM.value)
        for row in cellmap.cellmap: start_traces(row[0], Edge.name.LEFT.value)

        # find all closed contours
        Logger.log(logging.info, "Tracing closed contours...", sub=1)
        for row in cellmap.cellmap:
            for cell in row:
                for height in range(min(*cell.corners), max(*cell.corners) + 1):
                    for edge in cell.edges:
                        if height_within_difference(height, edge):
                            if not edge.contours[height]:
                                isoline = trace_from_here(cell, edge, height, closed=True)
                                if isoline:
                                    self.isolines.append(isoline)
                                break