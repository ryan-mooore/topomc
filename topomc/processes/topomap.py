import logging
import math
from topomc.process import Process

import matplotlib.path as mplpath
from scipy.spatial import ConvexHull
from topomc.common import yaml_open
from topomc.common.coordinates import Coordinates
from topomc.common.logger import Logger
from topomc.processes.helpers.cellmap import CellMap, Edge
from topomc.render import MapRender


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

        angle = TopoMap.perp_ang(b, c) - TopoMap.perp_ang(a, b)
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


class TopoMap(Process):
    @staticmethod
    def create_normal(point1, angle, length):
        point2 = Coordinates(None, None)
        point2.x = point1.x + length * math.sin(math.pi - angle)
        point2.y = point1.y + length * math.cos(math.pi - angle)
        return [point1, point2]

    @staticmethod
    def perp_ang(point1, point2):
        return math.atan2(point2.y - point1.y, point2.x - point1.x)

    def __init__(self, blockmap):
        super().__init__(blockmap)
        self.isolines = []
        self.taglines = []

        Logger.log(logging.info, "Creating cell matrix...")
        self.cellmap = CellMap(blockmap)
        Logger.log(logging.info, "Done", t=False)

        self.width =  self.cellmap.width
        self.height = self.cellmap.height

    def process(self):
        def traverse(cell, edge):
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
        
        def start_traces(cell, edgename):
            edge = cell.edges[edgename] 
            for height in range(edge.min_corner(), edge.max_corner() + 1): # start a trace for every height in the cell
                if not edge.contours[height]: # check that a contour hasn't already been traced to here 
                    isoline = trace_from_here(cell, cell.edges[edgename], height, OpenIsoline) #  and start the trace
                    if isoline: # check that the contour is actually a line
                        self.isolines.append(isoline) # add the contour

        # find all open contours (open contours will always touch the edge)
        Logger.log(logging.info, "Tracing open contours...", sub=1)
        for cell in self.cellmap.cellmap[0]: start_traces(cell, Edge.name.TOP.value)
        for row in self.cellmap.cellmap: start_traces(row[len(row) - 1], Edge.name.RIGHT.value)
        for cell in self.cellmap.cellmap[len(self.cellmap.cellmap) - 1]: start_traces(cell, Edge.name.BOTTOM.value)
        for row in self.cellmap.cellmap: start_traces(row[0], Edge.name.LEFT.value)

        # find all closed contours
        Logger.log(logging.info, "Tracing closed contours...", sub=1)
        for row in self.cellmap.cellmap:
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
        
            Logger.log(logging.info, "Creating taglines...", sub=1)
            for isoline in self.isolines:
                if isinstance(isoline, Depression):
                    if isoline.extremum:
                        smallest_angle = math.pi
                        vertices = []
                        x, y = MapRender.smoothen(isoline.vertices)
                        for a, b in zip(x, y):
                            vertices.append(Coordinates(a, b))

                        def get_angle_at_index(vertices, index):
                            a = vertices[index - 1] if index != 0 else vertices[-2]
                            b = vertice
                            c = vertices[index + 1] if index != len(vertices) - 1 else vertices[1]
                            angle = self.perp_ang(b, c) - self.perp_ang(a, b)
                            if angle < 0: angle += 2 * math.pi
                            return angle, a, b, c

                        for index, vertice in enumerate(vertices):
                            
                            curr_angle, *_ = get_angle_at_index(vertices, index)
                            if curr_angle < smallest_angle:
                                smallest_angle = curr_angle
                        
                        for index, vertice in enumerate(vertices):
                        
                            angle, a, b, c = get_angle_at_index(vertices, index)
                            if angle == smallest_angle:
                                theta = math.atan2(a.x - b.x, a.y - b.y)
                                if theta < 0: theta += 2 * math.pi
                                theta = math.pi - theta
                                ang = theta + smallest_angle / 2
                                normal = self.create_normal(b, ang, yaml_open.get("tagline length"))
                                break
