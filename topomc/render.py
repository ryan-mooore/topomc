from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy import interpolate
import numpy as np
import os
import logging

from topomc.marching_squares import Coordinates
from topomc.common import progressbar, yaml_open

class MapRender:
    def __init__(self, topomap):
        self.topomap = topomap

    def render(self):

        plt.figure("Preview")
        
        smoothness = yaml_open.get("smoothness")
        contour_index = yaml_open.get("index")
        save_loc = yaml_open.get("pdf save location")
        line_width = yaml_open.get("line width")
        if save_loc:
            save_loc = os.path.normpath(save_loc)
            if not save_loc.endswith(".pdf"):
                if save_loc.endswith(os.sep):
                    save_loc = save_loc + "map.pdf"
                else:
                    save_loc = save_loc + ".pdf"

        max_len = max(np.floor(self.topomap.width / 15), np.floor(self.topomap.height / 15))
        isolines_to_render = 0

        isolines_rendered = 0
        margin = 3

        for i in range (1):
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

                    IOF_INDEX_RATIO = 25/14
                    # if contour_index and heightplane.height % contour_index == 0:
                    #     plt.plot(x, y, "#D15C00", linewidth=line_width / 3 * IOF_INDEX_RATIO)
                    # else:
                    plt.plot(x, y, "#D15C00", linewidth=line_width / 3)
                except Exception as e:
                    pass

                isolines_rendered += 1
                if isolines_rendered % 50 == 0 or isolines_rendered == isolines_to_render:
                    progressbar._print(
                        isolines_rendered,
                        isolines_to_render,
                        2,
                        "isolines rendered"
                    )


        logging.info("Render: Loading matplotlib window...")
        print()


        plt.axis("off")

        axes = plt.gca()
        graph = plt.gcf()

        axes.set_aspect(1)
        axes.set_xlim(0, self.topomap.width)
        axes.set_ylim(0, self.topomap.height)

        scale_ratio = yaml_open.get("scale")
        divisor, scale = scale_ratio.split(":")
        scale = int(scale) / int(divisor)

        if save_loc:
            # units * 100(metres) / scale * inch conversion
            graph.set_size_inches(self.topomap.width * 100 / scale * 0.393701, self.topomap.height * 100 / scale * 0.393701)
            graph.savefig(save_loc)

        for line in axes.lines:
            line.set_linewidth(
                line.get_linewidth() * 2**(4 - np.log2(max_len)))

        window_size = yaml_open.get("preview size")
        graph.set_size_inches(8 * window_size, 8 * window_size)
        if graph.canvas.toolbar:
            graph.canvas.toolbar.pack_forget()
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        plt.show()

    def debug(self, heightmap):
        plt.figure("Preview")

        for value, isoline in enumerate(self.topomap.isolines):
            isoline.vertices = []
            for point in isoline.contour:
                (contour_coords, cell_coords) = point
                isoline.vertices.append((cell_coords.x + contour_coords.x,
                cell_coords.y + 1 - contour_coords.y))
            

            x = [vertice[0] for vertice in isoline.vertices]
            y = [vertice[1] for vertice in isoline.vertices]
        
            plt.plot(x, y, linewidth=1, marker="o", label=value)
            try:
                plt.text(x[0], y[0], value, color="#D15C00", size="20")
            except:
                pass

        axes = plt.gca()
        graph = plt.gcf()

        axes.set_xlim(0, 15)
        axes.set_ylim(0, 15)
        axes.invert_yaxis()
        axes.set_aspect(1)

        graph.set_size_inches(8, 8)
        plt.xticks(range(0, 15))
        plt.yticks(range(0, 15))
        # graph.canvas.toolbar.pack_forget()
        #plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.grid(color='#000', linestyle='-', linewidth=1, which="both")

        for y, row in enumerate(heightmap.heightmap):
            for x, cell in enumerate(row):
                plt.text(x, y, cell)

        logging.debug(f"App: Debugging chunk")
        logging.info("Render: Loading matplotlib window...")
        logging.disable(logging.DEBUG)
        print()

        save_loc = yaml_open.get("pdf save location")
        if save_loc:
            save_loc = os.path.normpath(save_loc)
            if not save_loc.endswith(".pdf"):
                if save_loc.endswith(os.sep):
                    save_loc = save_loc + "map.pdf"
                else:
                    save_loc = save_loc + ".pdf"
        if save_loc:
            graph.savefig(save_loc)

        plt.show()
