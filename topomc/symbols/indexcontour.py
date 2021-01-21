from topomc import app
from topomc.processes.topomap import ClosedIsoline, TopoMap
from topomc.render import MapRender
from topomc.symbol import Symbol


class IndexContour(Symbol):
    def __init__(self, processes):
        self.topomap = super().__init__(processes, klass=TopoMap)

        self.set_properties(
            type=Symbol.SymbolType.LINEAR,
            color="#D15C00",
            linewidth=2
        )
    
    def render(self):
        to_render = []
        interval = app.settings["Interval"]
        index = app.settings["Index"]
        smoothness = app.settings["Smoothness"]
        for isoline in self.topomap.closed_isolines + self.topomap.open_isolines:
            if isoline.height % index == 0:
                to_render.append(MapRender.smoothen(isoline.vertices, smoothness, is_closed=isinstance(isoline, ClosedIsoline)))
        return to_render
