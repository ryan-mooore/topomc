# marching squares algorithm for generating contour data
from typing import Tuple
from topomc.common import progressbar
from enum import Enum
import logging

class EdgeType(Enum):
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"
    RIGHT = "right"

class Edge:
    def min_corner(self): return min(self.corner1, self.corner2)
    def max_corner(self): return max(self.corner1, self.corner2)

    def __init__(self, corner1, corner2, x, y, edgetype):
        self.corner1 = corner1
        self.corner2 = corner2

        self.coords = Coordinates(x, y)

        self.type = edgetype

        self.contours = {}
        for possible_height in range(self.min_corner(), self.max_corner() + 1):
            self.contours[possible_height] = None

    def flip_edge(self) -> EdgeType:
        
        mapper = {
            EdgeType.TOP: EdgeType.BOTTOM,
            EdgeType.BOTTOM: EdgeType.TOP,
            EdgeType.LEFT: EdgeType.RIGHT,
            EdgeType.RIGHT: EdgeType.LEFT
        }

        return mapper[self.type]

    @property
    def direction(self):
        if self.corner1 < self.corner2:
            return 1
        elif self.corner1 > self.corner2:
            return -1
        else:
            return None


    @property
    def difference(self):
        if self.direction == 1:
            return self.corner2 - self.corner1
        elif self.direction == -1:
            return self.corner1 - self.corner2
        else:
            return 0

class Cell:
    def __init__(self, edges, coords):
        (tl, tr, br, bl) = edges
        self.edges = {
            EdgeType.LEFT:   Edge(bl, tl, 0, None, EdgeType.LEFT),
            EdgeType.TOP:    Edge(tl, tr, None, 1, EdgeType.TOP),
            EdgeType.RIGHT:  Edge(br, tr, 1, None, EdgeType.RIGHT),
            EdgeType.BOTTOM: Edge(bl, br, None, 0, EdgeType.BOTTOM)
        }
        self.coords = Coordinates(*coords)

        self.min_corner_height = min(tl, tr, bl, br)
        self.max_corner_height = max(tl, tr, bl, br)

    def get_possible_edges(self, edge):
        et = EdgeType
        if edge == et.LEFT: return [self.edges[etype] for etype in [et.TOP, et.BOTTOM, et.RIGHT]]
        if edge == et.TOP:   return [self.edges[etype] for etype in [et.RIGHT, et.LEFT, et.BOTTOM]]
        if edge == et.RIGHT: return [self.edges[etype] for etype in [et.TOP, et.BOTTOM, et.LEFT]]
        if edge == et.BOTTOM: return [self.edges[etype] for etype in [et.RIGHT, et.LEFT, et.TOP]]


class Isoline:
    def __init__(self):
        self.contour = []
        self.direction = 0
        self.closed = False

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Coordinates):
            return NotImplemented

        return self.x == other.x and self.y == other.y

    def get_list(self):
        return self.x, self.y

    def __repr__(self):
        return f"{self.x, self.y}"

class CellMap:
    def __init__(self, heightmap):

        self.cells = []

        self.width  = len(heightmap.heightmap[0]) - 1
        self.height = len(heightmap.heightmap)    - 1

        # cells_created = 0
        # cells_to_create = (len(heightmap.heightmap) - 1) * (len(heightmap.heightmap[0]) - 1)

        for z in range(self.height):
            cell_row = []
            for x in range(self.width):
                hm = heightmap.heightmap

                cell = Cell((
                        hm[z]    [x],      # top left
                        hm[z]    [x + 1],  # top right
                        hm[z + 1][x + 1],  # bottom right
                        hm[z + 1][x]       # bottom left
                    ), (x, z)
                )

                cell_row.append(cell)
            self.cells.append(cell_row)

class TopoMap:
    def __init__(self, cellmap):
        self.isolines = []

        self.width = cellmap.width
        self.height = cellmap.height

        def hop_to_next_cell(cell: Cell, edge: Edge) -> Cell:
            if edge.type == EdgeType.RIGHT:  return cellmap.cells[cell.coords.y][cell.coords.x + 1]
            if edge.type == EdgeType.LEFT:   return cellmap.cells[cell.coords.y][cell.coords.x - 1]
            if edge.type == EdgeType.BOTTOM: return cellmap.cells[cell.coords.y + 1][cell.coords.x]
            if edge.type == EdgeType.TOP:    return cellmap.cells[cell.coords.y - 1][cell.coords.x] 

            logging.critical(f"Tracing Error: could not find next cell for cell {cell.coords}")

        def has_hit_boundary(cell: Cell, edge: Edge) -> bool:
            
            et = edge.type
            pos = cell.coords

            if \
            et == EdgeType.LEFT   and pos.x == 0 or \
            et == EdgeType.TOP    and pos.y == 0 or \
            et == EdgeType.RIGHT  and pos.x == len(cellmap.cells[0]) - 1 or \
            et == EdgeType.BOTTOM and pos.y == len(cellmap.cells)    - 1:
                return True
            else: 
                return False

        def create_point_coords(edge: Edge, point: float) -> Coordinates:
            coords = Coordinates(edge.coords.x, edge.coords.y)

            if coords.x == None:
                coords.x = point
            if coords.y == None:
                coords.y = point
            
            return coords

        def has_self_closed(isoline, custom_check: Tuple=None):
            if isoline.closed:
                if len(isoline.contour) > 3:
                    if isoline.contour[1] == (custom_check if custom_check else isoline.contour[-1]):
                        return True
                    else:
                        return False

        def trace_from_here(cell, edge, height, closed=False) -> Isoline:
            if edge.min_corner() <= height < edge.max_corner(): # a contour starts at this edge at this height
                
                # create contour
                isoline = Isoline()
                if closed:
                    isoline.closed = True # this countour will not touch the edge; therefore must be closed
                else:
                    distance_from_edge = height - edge.min_corner()

                    point = distance_from_edge / edge.difference
                    if edge.direction == -1: point = 1 - point

                    edge.contours[height] = isoline
                    point_coords = create_point_coords(edge, point)
                    isoline.contour.append((point_coords, cell.coords))
                
                edge = cell.edges[edge.flip_edge()]

                # trace
                while True:
                    possible_edges = cell.get_possible_edges(edge.flip_edge())
                    for edge in possible_edges:
                        if edge.min_corner() <= height < edge.max_corner(): # a contour starts at this edge at this height

                            if edge.contours[height]: # found a contour already here
                                if isoline.closed:
                                    if edge.contours[height] == isoline: # found another part of the same contour
                                        distance_from_edge = height - edge.min_corner()
                                        point = distance_from_edge / edge.difference
                                        if edge.direction == -1: point = 1 - point
                                        point_coords = create_point_coords(edge, point)
                                        if has_self_closed(isoline, custom_check=(point_coords, cell.coords)):
                                            pass
                                        else:
                                            # have reached the same contour but not at the start.
                                            continue
                                    continue 
                                else:
                                    continue # move on, don't want to cross contour
                            
                            # set both adjacent cells' edges to point to the current countour
                            edge.contours[height] = isoline
                            if not has_hit_boundary(cell, edge):
                                hop_to_next_cell(cell, edge).edges[edge.flip_edge()].contours[height] = isoline

                            distance_from_edge = height - edge.min_corner()
                            point = distance_from_edge / edge.difference
                            if edge.direction == -1: point = 1 - point
                            point_coords = create_point_coords(edge, point)
                            isoline.contour.append((point_coords, cell.coords))

                            if has_self_closed(isoline) or has_hit_boundary(cell, edge):
                                return isoline
                            else:
                                cell = hop_to_next_cell(cell, edge)
                                break
                    else:
                        logging.critical(f"Routing Error at {cell.coords}")
                        break
                    if len(isoline.contour) > 50000:
                        logging.critical(f"Critical routing error with isoline starting at {repr(isoline.contour[0][1])}. Aborting this isoline")
                        break
        
        def start_traces(cell: Cell, edgetype: EdgeType) -> None:
            edge = cell.edges[edgetype] 
            for height in range(edge.min_corner(), edge.max_corner() + 1):
                if not edge.contours[height]: # no contour here already
                    isoline = trace_from_here(cell, cell.edges[edgetype], height)
                    if isoline:
                        self.isolines.append(isoline)
                else:
                    pass

        # find all open contours (open contours will always touch the edge)
        for cell in cellmap.cells[0]: 
            start_traces(cell, EdgeType.TOP)
        for row in cellmap.cells: 
            start_traces(row[len(row) - 1], EdgeType.RIGHT)
        for cell in cellmap.cells[len(cellmap.cells) - 1]: 
            start_traces(cell, EdgeType.BOTTOM)
        for row in cellmap.cells: 
            start_traces(row[0], EdgeType.LEFT)

        # find all closed contours
        for row in cellmap.cells:
            for cell in row:
                for height in range(cell.min_corner_height, cell.max_corner_height + 1):
                    for edge in cell.edges.values():
                        if edge.min_corner() <= height < edge.max_corner():
                            if not edge.contours[height]:
                                isoline = trace_from_here(cell, edge, height, closed=True)
                                if isoline:
                                    self.isolines.append(isoline)
                                break
        
        pass