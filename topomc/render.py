from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy import interpolate
import numpy as np
import os
from topomc.common.logger import Logger
import logging
from topomc.symbol import Symbol

from topomc.common import progressbar, yaml_open

class MapRender:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def get_settings(self):
        self.smoothness = yaml_open.get("smoothness")
        self.contour_index = yaml_open.get("index")
        self.save_loc = yaml_open.get("pdf save location")
        self.line_width = yaml_open.get("line width")

    def get_save_loc(self):
        if self.save_loc:
            save_loc = os.path.normpath(self.save_loc)
            if not save_loc.endswith(".pdf"):
                if save_loc.endswith(os.sep):
                    self.save_loc = save_loc + "map.pdf"
                else:
                    self.save_loc = save_loc + ".pdf" 

    def render(self, symbols):

        plt.figure("Preview")
        self.get_settings()
        self.get_save_loc()

        max_len = max(np.floor(self.width / 16), np.floor(self.height / 16))

        for symbol in symbols:
            if symbol.type == Symbol.type.LINEAR:
                renders = symbol.render()
                for x, y in renders:
                    plt.plot(x, y, symbol.color, linewidth=symbol.linewidth / 3)

        Logger.log(logging.info, "Loading matplotlib window...", t=False)
        print()


        plt.axis("off")

        axes = plt.gca()
        graph = plt.gcf()

        axes.set_aspect(1)
        axes.set_xlim(0, self.width)
        axes.set_ylim(0, self.height)

        scale_ratio = yaml_open.get("scale")
        divisor, scale = scale_ratio.split(":")
        scale = int(scale) / int(divisor)

        if self.save_loc:
            # units * 100(metres) / scale * inch conversion
            graph.set_size_inches(self.width * 100 / scale * 0.393701, self.height * 100 / scale * 0.393701)
            graph.savefig(self.save_loc)

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
