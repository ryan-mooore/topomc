import logging
from enum import Enum
from topomc.common.coordinates import Coordinates
from matplotlib import pyplot as plt
from svgpath2mpl import parse_path
from xml.dom import minidom
from os import path

from topomc.common.logger import Logger


class Symbol:
    settings = []

    def render(self, settings):
        raise NotImplementedError

    def debug(self, settings):
        Logger.log(
            logging.critical,
            f"debugging is not supported for {self.__class__.__name__}",
        )
        raise NotImplementedError

    def __init__(self, processes, klass):
        return next(proc for proc in processes if isinstance(proc, klass))

    def set_properties(self):
        raise NotImplementedError("Cannot set properties of unspecified symbol type")

    def plot(self):
        raise NotImplementedError("Cannot plot unspecified symbol type")


class AreaSymbol(Symbol):
    def set_properties(self, fillcolor, bordercolor, borderwidth):
        self.fillcolor = fillcolor
        self.bordercolor = bordercolor
        self.borderwidth = borderwidth / 3

    def plot(self, area):
        plt.fill(
            *Coordinates.to_list(area),
            facecolor=self.fillcolor,
            edgecolor=self.bordercolor,
            linewidth=self.borderwidth,
        )


class LinearSymbol(Symbol):
    def set_properties(self, color, linewidth):
        self.color = color
        self.linewidth = linewidth / 3

    def plot(self, line):
        plt.plot(*Coordinates.to_list(line), color=self.color, linewidth=self.linewidth)


class PointSymbol(Symbol):
    def set_properties(self, color, pointsize=1, icon=None):
        self.color = color
        if icon:
            self.icon = icon
        else:
            doc = minidom.parse(
                path.join(
                    path.dirname(__file__),
                    "assets",
                    "symbols",
                    f"{self.__class__.__name__}.svg",
                )
            )
            icon = parse_path(
                [p.getAttribute("d") for p in doc.getElementsByTagName("path")][0]
            )
            doc.unlink()

            for vertice in icon.vertices:
                vertice[1] = -vertice[1]
            icon.vertices -= icon.vertices.mean(axis=0)
            self.icon = icon

        self.pointsize = pointsize * 2

    def plot(self, point):
        plt.plot(
            point.x,
            point.y,
            color=self.color,
            marker=self.icon,
            markersize=self.pointsize,
            linewidth=0,
        )
