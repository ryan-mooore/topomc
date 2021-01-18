from topomc.symbols.contour import Contour

class IndexContour(Contour):
    def __init__(self, topomap) -> None:
        super().__init__()
        self.linewidth = 2
        self.topomap = topomap
    
    def build(self):
        pass