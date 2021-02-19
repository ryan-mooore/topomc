from topomc.common.coordinates import Coordinates
from topomc.processes.topomap import Depression, Hill, TopoMap
from topomc.symbol import PointSymbol


class Knoll(PointSymbol):
    def __init__(self, processes):
        self.topomap = super().__init__(processes, klass=TopoMap)

        self.set_properties(color="#BA5E1A")
    
    def render(self):
        
        def check_for_feature(isoline):
            if len(isoline.vertices) < 12 and isinstance(isoline, Hill):
                self.plot(Coordinates(
                    sum([p.x for p in isoline.vertices]) / len(isoline.vertices) + 0.5,
                    sum([p.y for p in isoline.vertices]) / len(isoline.vertices) + 0.5
                ))
                return True
            return False

        def search(isoline):
            if isoline.contains:
                for new_isoline in isoline.contains:
                    if not check_for_feature(isoline):
                        search(new_isoline)

        for isoline in self.topomap.topograph.base:
            if not check_for_feature(isoline):
                search(isoline)
