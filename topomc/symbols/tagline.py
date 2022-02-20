import math

from topomc.processes.topomap import Depression, TopoMap
from topomc.render import MapRender
from topomc.symbol import LinearSymbol


class Tagline(LinearSymbol):

    settings = ["tagline_length", "smoothness"]

    def __init__(self, processes):
        self.topomap = super().__init__(processes, klass=TopoMap)

        self.set_properties(color="#BA5E1A", linewidth=1)

    def render(self, tagline_length=1, smoothness=1):

        if tagline_length == 0:
            return

        def create_tagline(isoline):
            smallest_angle = math.pi
            vertices = MapRender.smoothen(isoline.vertices, smoothness)

            def get_angle_at_index(vertices, index):
                a = vertices[index - 1] if index != 0 else vertices[-2]
                b = vertice
                c = vertices[index +
                             1] if index != len(vertices) - 1 else vertices[1]
                angle = TopoMap.perp_ang(b, c) - TopoMap.perp_ang(b, a)
                if angle < 0:
                    angle += 2 * math.pi
                return angle, a, b, c

            for index, vertice in enumerate(vertices):

                curr_angle, *_ = get_angle_at_index(vertices, index)
                if curr_angle < smallest_angle:
                    smallest_angle = curr_angle

            for index, vertice in enumerate(vertices):

                angle, a, b, c = get_angle_at_index(vertices, index)
                if angle == smallest_angle:
                    theta = math.atan2(a.x - b.x, a.y - b.y)
                    if theta < 0:
                        theta += 2 * math.pi
                    theta = math.pi - theta
                    ang = theta + smallest_angle / 2
                    normal = TopoMap.create_normal(b, ang, tagline_length)
                    for point in normal:
                        point.x += 0.5
                        point.y += 0.5
                    self.plot(normal)
                    break

        for isoline in self.topomap.closed_isolines:
            if isinstance(isoline, Depression) and not isoline.small_feature:
                if isoline.last_large_depression:
                    create_tagline(isoline)
