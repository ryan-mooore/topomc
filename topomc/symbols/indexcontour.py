from topomc.processes.topomap import ClosedIsoline, TopoMap
from topomc.render import MapRender
from topomc.symbol import LinearSymbol


class IndexContour(LinearSymbol):
    settings = ["index", "smoothness"]

    def __init__(self, processes):
        self.topomap = super().__init__(processes, TopoMap)

        self.set_properties(color="#BA5E1A", linewidth=2)

    def render(self, index=5, smoothness=1):
        for isoline in self.topomap.closed_isolines + self.topomap.open_isolines:
            if isoline.height % index == 0:
                if isinstance(isoline, ClosedIsoline):
                    if isoline.small_feature == True:
                        continue
                for vertice in isoline.vertices:
                    vertice.x += 0.5
                    vertice.y += 0.5
                self.plot(
                    MapRender.smoothen(
                        isoline.vertices,
                        smoothness,
                        is_closed=isinstance(isoline, ClosedIsoline),
                    )
                )
