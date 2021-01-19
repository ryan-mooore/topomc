from topomc.symbol import Symbol
from topomc.render import MapRender
from topomc.common import yaml_open
from topomc.processes.topomap import ClosedIsoline, TopoMap

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
        interval = yaml_open.get("interval")
        for isoline in self.topomap.isolines:
            if isoline.height % interval == 0:
                to_render.append(MapRender.smoothen(isoline.vertices, is_closed=isinstance(isoline, ClosedIsoline)))
        return to_render