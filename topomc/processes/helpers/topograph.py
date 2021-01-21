import logging
from topomc.common.logger import Logger
import matplotlib.path as mplpath


class TopoGraph():
    def __init__(self, topomap):
        self.base = []
        self.extremes = []

        Logger.log(logging.info, "Stacking contours...", sub=3)
        for isoline in topomap.closed_isolines:
            isoline_in_base = self.isoline_in_list(isoline, self.base)
            if isoline_in_base:
                new_isoline = self.find_level(isoline, isoline_in_base)
                new_isoline.contains.append(isoline)
            else:
                self.base.append(isoline)

        Logger.log(logging.info, "Finding maxima and minima...", sub=3) 
        for isoline in self.base:
            self.find_extremes(isoline)

    def isoline_in_list(self, isoline, iist):
        for test in iist:
            path = mplpath.Path([c.to_tuple() for c in test.vertices])
            if path.contains_point((isoline.vertices[0].to_tuple())):
                return test
        return False
   
    def find_level(self, isoline, new_isoline):
        if not new_isoline.contains: return new_isoline
        result = self.isoline_in_list(isoline, new_isoline.contains)
        if result:
            new_isoline = result
            return self.find_level(isoline, new_isoline)
        else:
            return new_isoline
    
    def find_extremes(self, isoline):
        if isoline.contains:
            for new_isoline in isoline.contains:
                self.find_extremes(new_isoline)
        else:
            self.extremes.append(isoline)