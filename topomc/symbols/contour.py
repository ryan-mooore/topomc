from topomc.symbol import Symbol
from topomc.algorithms.marching_squares import CellMap, TopoMap
from scipy.ndimage import gaussian_filter1d
from topomc.common.logger import Logger
import logging

smoothness = 1
margin = 3

class Contour(Symbol):
    def build(self, blockmap):
        Logger.log(logging.info, "Creating cell matrix...")
        cellmap = CellMap(blockmap)
        Logger.log(logging.info, "Done", t=False)

        Logger.log(logging.info, "Tracing contours...", t=False)
        self.topomap = TopoMap(cellmap)
        Logger.log(logging.info, "Done", t=False)

    def render(self):
        to_render = []
        for isoline in self.topomap.isolines:
            isoline.vertices = []
            for point in isoline.contour:
                (contour_coords, cell_coords) = point
                isoline.vertices.append((cell_coords.x + contour_coords.x,
                self.topomap.height - cell_coords.y - 1 + contour_coords.y))

            x = [vertice[0] for vertice in isoline.vertices]
            y = [vertice[1] for vertice in isoline.vertices]

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
            except: pass

            to_render.append((x, y))
        return to_render

    def __init__(self):
        super().__init__(
            type=Symbol.type.LINEAR,
            color="#D15C00",
            linewidth=1
        )
