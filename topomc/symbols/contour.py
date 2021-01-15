from topomc.symbol import Symbol
from topomc.algorithms.marching_squares import CellMap, Coordinates, TopoMap
from scipy.ndimage import gaussian_filter1d
from topomc.common.logger import Logger
import logging
from matplotlib import pyplot as plt
import math

smoothness = 1
margin = 3
tagline_len = 0.8

class Contour(Symbol):
    def build(self, blockmap):
        self.blockmap = blockmap
        Logger.log(logging.info, "Creating cell matrix...")
        cellmap = CellMap(blockmap)
        Logger.log(logging.info, "Done", t=False)

        Logger.log(logging.info, "Tracing contours...", t=False)
        self.topomap = TopoMap(cellmap)

        self.p = []
        Logger.log(logging.info, "Creating taglines...", sub=1)
        for isoline in self.topomap.isolines:
            if isoline.extremum:
                if isoline.orientation == 'anti' and isoline.downslope == 'left' or \
                   isoline.orientation == 'clock' and isoline.downslope == 'right':
                    smallest_angle = math.pi
                    vertices = []
                    x, y = self.smooth(isoline)
                    for a, b in zip(x, y):
                        vertices.append(Coordinates(a, b))
                    if isoline.orientation == "clock":
                        vertices.reverse() # vertices will always be anticlockwise


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
                            newx = b.x + tagline_len * math.sin(math.pi - ang)
                            newy = b.y + tagline_len * math.cos(math.pi - ang)
                            new = Coordinates(newx, newy)
                            points.append(([b.x, new.x], [b.y, new.y]))
                            break
                    else:
                        Logger.log(logging.error, "No angle found to bind tagline to", t=False)

                    self.p.extend(points)
        Logger.log(logging.info, "Done", t=False)

    def smooth(self, isoline):
        x = [vertice.x for vertice in isoline.vertices]
        y = [vertice.y for vertice in isoline.vertices]

        try:
            if smoothness:
                if isoline.closed:
                    x_start, x_end = x[0:margin], x[-margin:]
                    y_start, y_end = y[0:margin], y[-margin:]
                    x = x_end + x + x_start
                    y = y_end + y + y_start

                x = gaussian_filter1d(x, smoothness)
                y = gaussian_filter1d(y, smoothness)

                if isoline.closed:
                    x = x[margin:-margin + 1]
                    y = y[margin:-margin + 1]
            return x, y


        except: pass
    def render(self):
        to_render = []
        for isoline in self.topomap.isolines:
            
            if isoline.extremum:
                if isoline.orientation == 'anti' and isoline.downslope == 'left' or \
                   isoline.orientation == 'clock' and isoline.downslope == 'right':
                    pass # TODO depression check
            to_render.append(self.smooth(isoline))
        to_render.extend(self.p)
        return to_render
    
    def debug(self, plot, text):
        
        for value, isoline in enumerate(self.topomap.isolines):
            x = [vertice.x for vertice in isoline.vertices]
            y = [vertice.y for vertice in isoline.vertices]

            plt.plot(x[0], y[0], "go")
            if isoline.closed:
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

            plot(x, y, linewidth=1, color="#000", label=value)

        for y, row in enumerate(self.blockmap.heightmap):
            for x, cell in enumerate(row):
                plt.text(x, y, cell)

    def __init__(self):
        super().__init__(
            type=Symbol.type.LINEAR,
            color="#D15C00",
            linewidth=1
        )
