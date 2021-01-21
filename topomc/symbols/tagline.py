import math

from topomc import app
from topomc.common.coordinates import Coordinates
from topomc.processes.topomap import Depression, TopoMap
from topomc.render import MapRender
from topomc.symbol import Symbol


class Tagline(Symbol):
    def __init__(self, processes):
        self.topomap = super().__init__(processes, klass=TopoMap)

        self.set_properties(
            type=Symbol.SymbolType.LINEAR,
            color="#D15C00",
            linewidth=1
        )
    
    def render(self):
        to_render = []
        length = app.settings["Tagline length"]
        smoothness = app.settings["Smoothness"]

        if length == 0:
            return

        for isoline in self.topomap.topograph.extremes:
            if isinstance(isoline, Depression):
                smallest_angle = math.pi
                vertices = []
                x, y = MapRender.smoothen(isoline.vertices, smoothness)
                for a, b in zip(x, y):
                    vertices.append(Coordinates(a, b))

                def get_angle_at_index(vertices, index):
                    a = vertices[index - 1] if index != 0 else vertices[-2]
                    b = vertice
                    c = vertices[index + 1] if index != len(vertices) - 1 else vertices[1]
                    angle = TopoMap.perp_ang(b, c) - TopoMap.perp_ang(b, a)
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
                        normal = TopoMap.create_normal(b, ang, length)
                        to_render.append(Coordinates.transpose_list(normal))
                        break
        return to_render
