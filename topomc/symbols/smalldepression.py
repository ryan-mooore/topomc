from topomc.common.coordinates import Coordinates
from topomc.processes.topomap import Depression, TopoMap
from topomc.symbol import PointSymbol

class SmallDepression(PointSymbol):
    def __init__(self, processes):
        self.topomap = super().__init__(processes, klass=TopoMap)

        self.set_properties(
            color="#BA5E1A",
            pointsize=1
        )
    
    def render(self):
        
        def check_for_feature(isoline):
            if len(isoline.vertices) < 12 and isinstance(isoline, Depression):
                x = [p.x for p in isoline.vertices]
                y = [p.y for p in isoline.vertices]
                self.plot(Coordinates(
                    sum(x) / len(isoline.vertices),
                    sum(y) / len(isoline.vertices)
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