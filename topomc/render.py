import logging
import os

import numpy as np
from matplotlib import pyplot as plt
from scipy.ndimage.filters import gaussian_filter1d

from topomc.common.coordinates import Coordinates
from topomc.common.logger import Logger

MARGIN = 3


class MapRender:

    settings = ["smoothness", "contour_index", "save_location", "scale", "preview_size"]

    def __init__(
        self,
        width,
        height,
        world,
        smoothness=1,
        contour_index=5,
        save_location=".",
        scale="1:1000",
        preview_size=1,
    ):
        self.width = width
        self.height = height
        self.world = world
        self.smoothness = smoothness
        self.contour_index = contour_index
        self.scale = scale
        self.window_size = preview_size
        self.get_save_loc(save_location)

        plt.figure(f"Map of {self.world}")

        self.max_len = max(np.floor(self.width / 16), np.floor(self.height / 16))

    def get_save_loc(self, loc):
        self.save_loc = None
        if loc:
            save_loc = os.path.abspath(loc)
            if not save_loc.endswith(".pdf"):
                if os.path.isdir(save_loc):
                    self.save_loc = save_loc + os.sep + "map.pdf"
                else:
                    self.save_loc = save_loc + ".pdf"

    @staticmethod
    def smoothen(iist, smoothness, is_closed=True):
        x, y = Coordinates.to_list(iist)

        if smoothness:
            if is_closed:
                x_start, x_end = x[0:MARGIN], x[-MARGIN:]
                y_start, y_end = y[0:MARGIN], y[-MARGIN:]
                x = x_end + x + x_start
                y = y_end + y + y_start

            x = gaussian_filter1d(x, smoothness)
            y = gaussian_filter1d(y, smoothness)

            if is_closed:
                x = x[MARGIN : -MARGIN + 1]
                y = y[MARGIN : -MARGIN + 1]
        return Coordinates.from_list(x, y)

    def show(self):
        plt.axis("off")

        axes = plt.gca()
        graph = plt.gcf()

        axes.set_aspect(1)
        axes.set_xlim(0, self.width)
        axes.set_ylim(0, self.height)
        axes.invert_yaxis()

        divisor, scale = self.scale.split(":")
        scale = int(scale) / int(divisor)

        if self.save_loc:
            # units * 100(metres) / scale * inch conversion
            graph.set_size_inches(
                self.width * 100 / scale * 0.393701,
                self.height * 100 / scale * 0.393701,
            )
            graph.savefig(self.save_loc, format="pdf")

        for line in axes.get_lines():
            line.set_linewidth(line.get_linewidth() * 2 ** (4 - np.log2(self.max_len)))
        for line in [line for line in axes.get_lines() if line.get_marker() != "None"]:
            line.set_markersize(
                line.get_markersize() * 2 ** (4 - np.log2(self.max_len))
            )

        graph.set_size_inches(8 * self.window_size, 8 * self.window_size)
        if graph.canvas.toolbar:
            try:
                graph.canvas.toolbar.pack_forget()
            except AttributeError:
                pass
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

        Logger.log_done()
        Logger.log(logging.info, "Showing preview...", time_it=False)
        plt.show()
        Logger.log_done()

    def debug(self, symbol):
        plt.close()  # close current figure
        plt.figure(f"Debugging chunk {'x'} {'z'}")

        axes = plt.gca()
        graph = plt.gcf()

        axes.set_xlim(0, 15)
        axes.set_ylim(0, 15)
        axes.invert_yaxis()
        axes.set_aspect(1)

        graph.set_size_inches(8, 8)
        plt.xticks(range(0, 15))
        plt.yticks(range(0, 15))
        plt.grid(color="#000", linestyle="-", linewidth=1, which="both")

        symbol.debug()

        Logger.log(logging.info, "Showing preview...", time_it=False)
        print()

        if self.save_loc:
            graph.savefig(self.save_loc, format="pdf")

        plt.show()
