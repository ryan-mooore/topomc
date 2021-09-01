from topomc.common.coordinates import Coordinates
from topomc.processes.topomap import Depression, TopoMap
from topomc.symbol import PointSymbol


class Pit(PointSymbol):

    settings = ["steep_features_threshold"]

    def __init__(self, processes):
        self.topomap = super().__init__(processes, klass=TopoMap)

        self.set_properties(color="#BA5E1A", pointsize=1.8)

    def render(self, steep_features_threshold=3):

        for isoline in self.topomap.closed_isolines:
            if isoline.small_feature and isinstance(isoline, Depression):
                if isoline.first_small_feature:
                    if isoline.depth >= steep_features_threshold:
                        self.plot(
                            Coordinates(
                                sum([p.x for p in isoline.vertices])
                                / len(isoline.vertices)
                                + 0.5,
                                sum([p.y for p in isoline.vertices])
                                / len(isoline.vertices)
                                + 0.5,
                            )
                        )
