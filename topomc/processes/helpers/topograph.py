import logging
from topomc.common.logger import Logger
import matplotlib.path as mplpath
from topomc.processes import topomap as tm
from topomc import app

class TopoGraph():
    def __init__(self, topomap):
        self.base = []

        Logger.log(logging.info, "Stacking contours...", sub=3)
        for isoline in topomap.closed_isolines:
            
            isoline.extremum = False
            isoline.small_feature = False
            isoline.last_large_feature = False

            isoline_in_base = self.isoline_in_list(isoline, self.base)
            if isoline_in_base:
                new_isoline = self.find_level(isoline, isoline_in_base)
                new_isoline.contains.append(isoline)
            else:
                self.base.append(isoline)

        Logger.log(logging.info, "Finding maxima and minima...", sub=3) 
        for isoline in self.base:
            tmp_isoline = tm.Isoline(0)
            tmp_isoline.extremum = False
            tmp_isoline.small_feature = False
            tmp_isoline.last_large_feature = False
            tmp_isoline.contains = [isoline]
            self.find_extremes(tmp_isoline, 0)

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
    
    def find_extremes(self, isoline, depth):

        if not isoline.small_feature: 
            if isinstance(isoline, tm.Depression):
                isoline.last_large_depression = True
            isoline.last_large_feature = True

        if isoline.contains:
            for new_isoline in isoline.contains:
                if len(new_isoline.vertices) < app.settings["Small features threshold"]:
                    new_isoline.small_feature = True # found small feature
                    if isoline.small_feature: # if current feature is small as well just keep searching
                        new_isoline.first_small_feature = False
                        return self.find_extremes(new_isoline, depth + 1)
                    else:
                        new_isoline.first_small_feature = True
                        new_depth = self.find_extremes(new_isoline, depth + 1) # save depth as var to test for pit
                        new_isoline.depth = new_depth  - depth
                elif isinstance(isoline, tm.Depression) and isinstance(new_isoline, tm.Depression): 
                    isoline.last_large_depression = False # found another depression so not a minima
                    isoline.last_large_feature = False
                    self.find_extremes(new_isoline, depth + 1)
                else:
                    isoline.last_large_feature = False
                    self.find_extremes(new_isoline, depth + 1)
        else:
            isoline.extremum = True
            return depth