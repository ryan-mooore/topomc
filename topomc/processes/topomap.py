import logging
import math
from topomc.processes.helpers.topograph import TopoGraph

from scipy.spatial import ConvexHull
from topomc.common.coordinates import Coordinates
from topomc.common.logger import Logger
from topomc.process import Process
from topomc.processes.helpers.cellmap import CellMap, Edge


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
            if len(angles) == 3:
                break
        a, b, c = angles

        angle = TopoMap.perp_ang(b, c) - TopoMap.perp_ang(a, b)
        if angle < math.pi:
            # orientation is anti-clockwise
            if self.downslope == "right":
                return Hill(self)
            else:
                return Depression(self)
        else:  # angle > math.pi:
            # orientation is clockwise

            self.vertices.reverse()  # ensure that vertices will always be anticlockwise

            if self.downslope == "right":
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
        self.contains = []


class Hill(ClosedIsoline):
    def __init__(self, isoline):
        self.vertices = isoline.vertices
        self.height = isoline.height
        self.extremum = None
        self.contains = []


class TopoMap(Process):

    settings = ["interval", "phase", "tag_length", "small_features_threshold"]

    @staticmethod
    def create_normal(point1, angle, length):
        point2 = Coordinates(None, None)
        point2.x = point1.x + length * math.sin(math.pi - angle)
        point2.y = point1.y + length * math.cos(math.pi - angle)
        return [point1, point2]

    @staticmethod
    def perp_ang(point1, point2):
        return math.atan2(point2.y - point1.y, point2.x - point1.x)

    def __init__(
            self,
            blockmap,
            interval=1,
            phase=0,
            tag_length=1,
            small_features_threshold=14):
        super().__init__(blockmap)
        self.open_isolines = []
        self.closed_isolines = []

        Logger.log(
            logging.info,
            "Running CellMap subprocess...",
            sub=2,
            time_it=False)
        self.cellmap = CellMap(blockmap)

        self.width = self.cellmap.width
        self.height = self.cellmap.height

        self.interval = interval
        self.phase = phase
        self.tag_length = tag_length
        self.small_features_threshold = small_features_threshold

    def process(self):
        def traverse(cell, edge):
            cells = [*edge.cells]
            cells.remove(cell)
            return cells[0]

        def get_point_pos(height, edge):
            point = (height - edge.min_corner() + 1) / (edge.difference + 1)
            if edge.direction == -1:
                point = 1 - point
            return point

        def height_within_difference(height, edge):
            return (
                edge.min_corner() <= height < edge.max_corner()
            )  # a contour starts at this edge at this height

        def find_direction(first, second):
            if len(first.cells) == 1:
                if first.axis == "x" and first.cells[0].coords.y == 0:
                    return "left" if first.direction == -1 else "right"
                elif first.axis == "x" and first.cells[0].coords.y == self.height - 1:
                    return "left" if first.direction == 1 else "right"
                elif first.axis == "y" and first.cells[0].coords.x == 0:
                    return "left" if first.direction == 1 else "right"
                elif first.axis == "y" and first.cells[0].coords.x == self.width - 1:
                    return "left" if first.direction == -1 else "right"
            else:
                if first.axis == "x":
                    if first.cells[0] in second.cells:  # moving up
                        return "left" if first.direction == 1 else "right"
                    else:
                        return "left" if first.direction == -1 else "right"
                if first.axis == "y":
                    if first.cells[0] in second.cells:  # moving left
                        return "left" if first.direction == -1 else "right"
                    else:
                        return "left" if first.direction == 1 else "right"

        def add_point(isoline, height, edge, cell_coords):
            # local_coords = get_local_coords(height, edge)
            # isoline.contour.append((local_coords, cell_coords))
            if edge.axis == "x":
                vertice = Coordinates(
                    cell_coords.x + get_point_pos(height, edge),
                    edge.axis_pos,  # on an x axis edge so y is a known and whole number
                )
            else:  # edge.axis == "y":
                vertice = Coordinates(
                    edge.axis_pos,  # on an y axis edge so x is a known and whole number
                    cell_coords.y + get_point_pos(height, edge),
                )

            if hasattr(isoline, "edge_for_finding_direction"):
                isoline.downslope = find_direction(
                    isoline.edge_for_finding_direction, edge
                )
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
                    # sort by adjacent first, then opposite (to avoid
                    # crossover)
                    edges.sort(key=lambda e: e.axis == edge.axis)
                    for edge in edges:
                        if height_within_difference(height, edge):
                            if edge.contours[
                                height
                            ]:  # if a contour at the same height exists
                                # we only need to consider this edge if the
                                # isoline needs to be closed and is the same
                                # one we are tracing
                                if (isinstance(isoline, ClosedIsoline)
                                        and edge.contours[height]["isoline"] == isoline):
                                    if "start" in edge.contours[height]:
                                        add_point(
                                            isoline, height, edge, cell.coords)
                                        return (isoline := isoline.get_type())
                                        # if no then we have reached the same
                                        # contour but haven't looped back to
                                        # the start yet. Try another edge
                                continue  # if the contour does not need to be closed we don't care. we can't go to this edge. Try another edge
                            else:
                                pass
                                # no existing contour, easy trace to this edge

                            edge.contours[height][
                                "isoline"
                            ] = isoline  # mark the edge as visited
                            add_point(
                                isoline, height, edge, cell.coords
                            )  # and add the coordinates to the contour

                            if (
                                len(edge.cells) == 1
                            ):  # if the boundary has been hit the contour is complete
                                return isoline
                            else:
                                # otherwise trace again!
                                cell = traverse(cell, edge)
                                break  # go to next cell
                    else:
                        # this should never occur. if it does it means that
                        # there were no edges to trace to and the contour has
                        # to end prematurely
                        Logger.log(
                            logging.error, f"Routing Error at {cell.coords}")
                        break  # do not draw the contour

        def start_traces(cell, edgename):
            edge = cell.edges[edgename]
            for height in range(
                edge.min_corner(), edge.max_corner() + 1
            ):  # start a trace for every height in the cell
                if (
                    height % (self.interval + self.phase) == 0
                ):  # check contour is at correct interval
                    # check that a contour hasn't already been traced to here
                    if not edge.contours[height]:
                        isoline = trace_from_here(
                            cell, cell.edges[edgename], height, OpenIsoline
                        )  # and start the trace
                        if isoline:  # check that the contour is actually a line
                            self.open_isolines.append(isoline)

        # find all open contours (open contours will always touch the edge)
        Logger.log(logging.info, "Tracing open contours...", sub=2)
        for cell in self.cellmap.cellmap[0]:
            start_traces(cell, Edge.name.TOP.value)
        for row in self.cellmap.cellmap:
            start_traces(row[len(row) - 1], Edge.name.RIGHT.value)
        for cell in self.cellmap.cellmap[len(self.cellmap.cellmap) - 1]:
            start_traces(cell, Edge.name.BOTTOM.value)
        for row in self.cellmap.cellmap:
            start_traces(row[0], Edge.name.LEFT.value)

        # find all closed contours
        Logger.log(logging.info, "Tracing closed contours...", sub=2)
        for row in self.cellmap.cellmap:
            for cell in row:
                for edge in cell.edges:
                    if edge.direction == 1:
                        for height in range(edge.corner1, edge.corner2):
                            if not edge.contours[height]:
                                isoline = trace_from_here(
                                    cell, edge, height, ClosedIsoline
                                )
                                if isoline:
                                    self.closed_isolines.append(isoline)
                    if edge.direction == -1:
                        for height in range(
                                edge.corner1 - 1, edge.corner2 - 1, -1):
                            if not edge.contours[height]:
                                isoline = trace_from_here(
                                    cell, edge, height, ClosedIsoline
                                )
                                if isoline:
                                    self.closed_isolines.append(isoline)

        # find extremus
        if self.tag_length:  # this step is only needed if taglines are on
            Logger.log(
                logging.info,
                "Running TopoGraph subprocess...",
                sub=2,
                time_it=False)
            self.topograph = TopoGraph(
                self, small_features_threshold=self.small_features_threshold
            )
            pass
