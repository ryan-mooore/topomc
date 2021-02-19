import math

from matplotlib import pyplot as plt
from topomc import app
from topomc.common.coordinates import Coordinates
from topomc.processes.topomap import ClosedIsoline, Hill, OpenIsoline, TopoMap
from topomc.render import MapRender
from topomc.symbol import LinearSymbol


class Contour(LinearSymbol):
    def __init__(self, processes):
        self.topomap = super().__init__(processes, klass=TopoMap)

        self.set_properties(
            color="#BA5E1A",
            linewidth=1
        )

    def render(self):
        interval = app.settings["Interval"]
        smoothness = app.settings["Smoothness"]
        index = app.settings["Index"]
        for isoline in self.topomap.closed_isolines + self.topomap.open_isolines:
            if isoline.height % index and len(isoline.vertices) >= 12:
                self.plot(MapRender.smoothen(isoline.vertices, smoothness, is_closed=isinstance(isoline, ClosedIsoline)))

    def debug(self):
        for value, isoline in enumerate(self.topomap.closed_isolines + self.topomap.open_isolines):
            x, y = Coordinates.to_list(isoline.vertices)

            plt.plot(x[0], y[0], "go") # plot green line at start of contour
            if isinstance(isoline, ClosedIsoline):
                plt.plot(x[len(x) - 2], y[len(y) - 2], "ro") # add red point 1 point away from end so points are not on top of each other
            else:
                plt.plot(x[len(x) - 1], y[len(y) - 1], "ro") # add red point at end for OpenIsoline

            # left by default
            for point1, point2 in zip(isoline.vertices, isoline.vertices[1:]):
                point_middle = Coordinates(
                    (point1.x + point2.x) / 2,
                    (point1.y + point2.y) / 2
                )
                normal_ang = TopoMap.perp_ang(point1, point2)
                if isinstance(isoline, OpenIsoline):
                    if isoline.downslope == "right":
                        normal_ang += math.pi # add 180 if downslope is on other side
                elif isinstance(isoline, Hill): # all ClosedIsolines are anti-clockwise, so hills have downslope on right
                    normal_ang += math.pi

                normal = TopoMap.create_normal(point_middle, normal_ang, 0.2)
                plt.plot(*Coordinates.to_list(normal), color="#000") # plot tags

            plt.plot(x, y, linewidth=1, color="#000") # plot isoline
            plt.text(x[0], y[0], value, color="g")

        for y, row in enumerate(self.topomap.blockmap.heightmap):
            for x, cell in enumerate(row):
                plt.text(x, y, cell) # plot heightmap values

