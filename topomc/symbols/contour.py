import logging
import math
import copy
from enum import Enum
from topomc.common import yaml_open

import matplotlib.path as mplpath
from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.spatial import ConvexHull

from topomc.common.logger import Logger
from topomc.common.coordinates import Coordinates
from topomc.symbol import Symbol

margin = 3
taglines = True

class Contour(Symbol):
    def __init__(self):
        super().__init__(
            type=Symbol.SymbolType.LINEAR,
            color="#D15C00",
            linewidth=1
        )

    def build(self, blockmap):
        self.blockmap = blockmap
        Logger.log(logging.info, "Creating cell matrix...")
        cellmap = CellMap(blockmap)
        Logger.log(logging.info, "Done", t=False)

        Logger.log(logging.info, "Tracing contours...", t=False)
        self.topomap = TopoMap(cellmap)
        
        self.p = []
        if yaml_open.get("tagline length"):
            Logger.log(logging.info, "Creating taglines...", sub=1)
            for isoline in self.topomap.isolines:
                if isinstance(isoline, Depression):
                    if isoline.extremum:
                        smallest_angle = math.pi
                        vertices = []
                        x, y = self.smooth(isoline)
                        for a, b in zip(x, y):
                            vertices.append(Coordinates(a, b))

                        def get_angle_at_index(vertices, index):
                            a = vertices[index - 1] if index != 0 else vertices[-2]
                            b = vertice
                            c = vertices[index + 1] if index != len(vertices) - 1 else vertices[1]
                            angle = math.atan2(c.y -b.y, c.x -b.x) - math.atan2(a.y-b.y, a.x-b.x)
                            if angle < 0: angle += 2 * math.pi
                            return angle, a, b, c

                        for index, vertice in enumerate(vertices):
                            
                            curr_angle, *_ = get_angle_at_index(vertices, index)
                            if curr_angle < smallest_angle:
                                smallest_angle = curr_angle
                        
                        points = []
                        for index, vertice in enumerate(vertices):
                        
                            angle, a, b, c = get_angle_at_index(vertices, index)
                            if angle == smallest_angle:
                                theta = math.atan2(a.x - b.x, a.y - b.y)
                                if theta < 0: theta += 2 * math.pi
                                theta = math.pi - theta
                                ang = theta + smallest_angle / 2
                                newx = b.x + yaml_open.get("tagline length") * math.sin(math.pi - ang)
                                newy = b.y + yaml_open.get("tagline length") * math.cos(math.pi - ang)
                                new = Coordinates(newx, newy)
                                points.append(([b.x, new.x], [b.y, new.y]))
                                break
                        else:
                            Logger.log(logging.error, "No angle found to bind tagline to", t=False)

                        self.p.extend(points)
            Logger.log(logging.info, "Done", t=False)

    def build_child(self):
        index_isolines = []
        new_isolines = []
        isolines = self.topomap.isolines
        for isoline in isolines:
            if isoline.height % yaml_open.get("index"):
                new_isolines.append(isoline)
            else:
                index_isolines.append(isoline)
        
        self.topomap.isolines = new_isolines
        new_topomap = copy.deepcopy(self.topomap)
        new_topomap.isolines = index_isolines
        return new_topomap


    def smooth(self, isoline):
        x = [vertice.x for vertice in isoline.vertices]
        y = [vertice.y for vertice in isoline.vertices]

        try:
            if yaml_open.get("smoothness"):
                if isinstance(isoline, ClosedIsoline):
                    x_start, x_end = x[0:margin], x[-margin:]
                    y_start, y_end = y[0:margin], y[-margin:]
                    x = x_end + x + x_start
                    y = y_end + y + y_start

                x = gaussian_filter1d(x, yaml_open.get("smoothness"))
                y = gaussian_filter1d(y, yaml_open.get("smoothness"))

                if isinstance(isoline, ClosedIsoline):
                    x = x[margin:-margin + 1]
                    y = y[margin:-margin + 1]
            return x, y

        except Exception as e: Logger.log(logging.error, e)


    def render(self):
        to_render = []
        for isoline in self.topomap.isolines:
            to_render.append(self.smooth(isoline))
        if hasattr(self, "p"):
            to_render.extend(self.p)
        return to_render


    def debug(self):
        for value, isoline in enumerate(self.topomap.isolines):
            x = [vertice.x for vertice in isoline.vertices]
            y = [vertice.y for vertice in isoline.vertices]

            plt.plot(x[0], y[0], "go")
            if isinstance(isoline, OpenIsoline):
                plt.plot(x[len(x) - 2], y[len(y) - 2], "ro")
            else:
                plt.plot(x[len(x) - 1], y[len(y) - 1], "ro")


            # left by default
            for point1, point2 in zip(isoline.vertices, isoline.vertices[1:]):
                middle = Coordinates((point1.x + point2.x) / 2, (point2.y + point1.y) / 2)
                gradient = math.atan2(point2.x - point1.x, point2.y - point1.y) * -1
                normal = gradient + math.pi / 2
                if isoline.downslope == "right":
                    normal += math.pi
                newx = 0.2 * math.sin(math.pi - normal)
                newy = 0.2 * math.cos(math.pi - normal)
                plt.plot([middle.x, middle.x + newx], [middle.y, middle.y + newy], color="#000")

            plt.plot(x, y, linewidth=1, color="#000", label=value)

        for y, row in enumerate(self.blockmap.heightmap):
            for x, cell in enumerate(row):
                plt.text(x, y, cell)


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
        return f"Cell {self.corners[0]}==={self.corners[1]}---{self.corners[2]}==={self.corners[3]} at coordinates {self.coords!r}"

class Isoline:
    def __init__(self, height) -> None:
        self.vertices = []
        self.downslope = None
        self.height = height
    
    def __repr__(self) -> str:
        return "---".join([repr(cell[1]) for cell in self.contour])

class ClosedIsoline(Isoline):
    def __init__(self, height) -> None:
        super().__init__(height)

    def get_type(self):
        hull = ConvexHull([(c.x, c.y) for c in self.vertices])
        angles = []
        for index, vertice in enumerate(self.vertices):
            if index in hull.vertices:
                angles.append(vertice)
            if len(angles) == 3: break
        a, b, c = angles

        angle = math.atan2(c.y -b.y, c.x -b.x) - math.atan2(a.y-b.y, a.x-b.x)
        if angle < math.pi:
            #orientation is anti-clockwise
            if self.downslope == 'right':
                return Hill(self)
            else:
                return Depression(self)
        else: # angle > math.pi:
            #orientation is clockwise

            self.vertices.reverse() # ensure that vertices will always be anticlockwise

            if self.downslope == 'right':
                return Depression(self)
            else:
                return Hill(self)


class OpenIsoline(Isoline):
    def __init__(self, height) -> None:
        super().__init__(height)

class Depression(ClosedIsoline):
    def __init__(self, isoline):
        self.vertices = isoline.vertices
        self.height = isoline.height
        self.extremum = None

class Hill(ClosedIsoline):
    def __init__(self, isoline):
        self.vertices = isoline.vertices
        self.height = isoline.height
        self.extremum = None

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
                if x == 0: self._link_edge(cell, Edge(bl, tl, 0, "y"))
                else:      self._link_edge(cell, cell_row[x - 1].edges[Edge.name.RIGHT.value])
                # top
                if z == 0: self._link_edge(cell, Edge(tl, tr, 0, "x"))
                else:      self._link_edge(cell, self.cellmap[z - 1][x].edges[Edge.name.BOTTOM.value])
                # right
                self._link_edge(cell, Edge(br, tr, cell.coords.x + 1, "y"))
                # bottom
                self._link_edge(cell, Edge(bl, br, cell.coords.y + 1, "x"))

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
        
        def get_point_pos(height, edge):
            point = (height - edge.min_corner() + 1) / (edge.difference + 1)
            if edge.direction == -1: point = 1 - point
            return point

        def height_within_difference(height, edge):
            return edge.min_corner() <= height < edge.max_corner() # a contour starts at this edge at this height

        def find_direction(first, second):
            if len(first.cells) == 1:
                if first.axis == 'x' and first.cells[0].coords.y == 0:
                    return 'left' if first.direction == -1 else 'right'
                elif first.axis == 'x' and first.cells[0].coords.y == self.height - 1:
                    return 'left' if first.direction == 1 else 'right'
                elif first.axis == 'y' and first.cells[0].coords.x == 0:
                    return 'left' if first.direction == -1 else 'right'
                elif first.axis == 'y' and first.cells[0].coords.x == self.width - 1:
                    return 'left' if first.direction == 1 else 'right'
                else:
                    logging.critical("error")
                    return None
            else:
                if first.axis == 'x':
                    if first.cells[0] in second.cells: # moving up
                        return 'left' if first.direction == 1 else 'right'
                    else:
                        return 'left' if first.direction == -1 else 'right'
                if first.axis == 'y':
                    if first.cells[0] in second.cells: # moving left
                        return 'left' if first.direction == 1 else 'right'
                    else:
                        return 'left' if first.direction == -1 else 'right'


        def add_point(isoline, height, edge, cell_coords):
            # local_coords = get_local_coords(height, edge)
            # isoline.contour.append((local_coords, cell_coords))
            if edge.axis == "x":
                vertice = Coordinates(
                    cell_coords.x + get_point_pos(height, edge),
                    edge.axis_pos # on an x axis edge so y is a known and whole number
                )
            else: # edge.axis == "y":
                vertice = Coordinates(
                    edge.axis_pos, # on an y axis edge so x is a known and whole number
                    cell_coords.y + 1 - get_point_pos(height, edge)
                )
            
            if hasattr(isoline, "edge_for_finding_direction"):
                isoline.downslope = find_direction(isoline.edge_for_finding_direction, edge)
                del isoline.edge_for_finding_direction

            isoline.vertices.append(vertice)

        def trace_from_here(cell, edge, height, isoline_type) -> Isoline:
            if height_within_difference(height, edge):
                
                isoline = isoline_type(height)

                edge.contours[height]["isoline"] = isoline
                edge.contours[height]["start"] = True
                add_point(isoline, height, edge, cell.coords)
                isoline.edge_for_finding_direction = edge

                # trace
                while True:
                    edges = [*cell.edges]
                    edges.remove(edge)
                    edges.sort(key=lambda e: e.axis == edge.axis) # sort by adjacent first, then opposite (to avoid crossover)
                    for edge in edges:
                        if height_within_difference(height, edge):
                            if edge.contours[height]: # if a contour at the same height exists
                                if isinstance(isoline, ClosedIsoline) and edge.contours[height]["isoline"] == isoline: # we only need to consider this edge if the isoline needs to be closed and is the same one we are tracing
                                    if "start" in edge.contours[height]:
                                        add_point(isoline, height, edge, cell.coords)
                                        return (isoline := isoline.get_type())
                                        # if no then we have reached the same contour but haven't looped back to the start yet. Try another edge
                                continue # if the contour does not need to be closed we don't care. we can't go to this edge. Try another edge
                            else:
                                pass
                                # no existing contour, easy trace to this edge

                            edge.contours[height]["isoline"] = isoline # mark the edge as visited
                            add_point(isoline, height, edge, cell.coords) # and add the coordinates to the contour

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
                    isoline = trace_from_here(cell, cell.edges[edgename], height, OpenIsoline) #  and start the trace
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
                                isoline = trace_from_here(cell, edge, height, ClosedIsoline)
                                if isoline:
                                    self.isolines.append(isoline)
                                break

        def check_isoline(isoline):
            for test_isoline in self.isolines:
                if isinstance(test_isoline, ClosedIsoline):

                    path = mplpath.Path([c.to_tuple() for c in isoline.vertices])
                    # TODO consider contains_path
                    if path.contains_point((test_isoline.vertices[0].to_tuple())): # if any of the test isoline's vertices are inside the current one
                        isoline.extremum = False # the current one is not an extremum
                        return check_isoline(test_isoline) # move to next one
                    else:
                        pass
            isoline.extremum = True

        # find extremus
        if yaml_open.get("tagline length"): # this step is only needed if taglines are on
            Logger.log(logging.info, "Finding maxima and minima...", sub=1)
            isoline = None
            for isoline in self.isolines:
                if isinstance(isoline, ClosedIsoline):
                    if isoline.extremum == None:
                        check_isoline(isoline) # check it
