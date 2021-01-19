class Process:
    def __init__(self, blockmap):
        self.blockmap = blockmap

        self.width  = blockmap.width
        self.height = blockmap.height

    def process(self):
        return NotImplementedError