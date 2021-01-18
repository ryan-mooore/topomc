from enum import Enum
from topomc.symbols import *

class Symbol:

    class SymbolType(Enum):
        POINT = 0
        LINEAR = 1
        AREA = 2
    type = SymbolType

    @classmethod
    def from_type(symbol_type):
        symbol = Symbol()
        symbol.type = symbol_type

    def build(self, blockmap):
        raise NotImplementedError

    def build_child(self, child):
        raise NotImplementedError

    def render(self, blockmap):
        raise NotImplementedError

    def debug(self, blockmap):
        raise NotImplementedError

    def __init__(self, type, color, linewidth) -> None:
        self.type = type
        self.color = color
        self.linewidth = linewidth