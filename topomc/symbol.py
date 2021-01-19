import logging
from enum import Enum

from topomc.common.logger import Logger


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

    def render(self, blockmap):
        raise NotImplementedError

    def debug(self, blockmap):
        Logger.log(logging.critical, f"debugging is not supported for {self.__class__.__name__}")
        raise NotImplementedError

    def __init__(self, processes, klass):
        return next(proc for proc in processes if isinstance(proc, klass))

    def set_properties(self, type=None, color=None, linewidth=None):
        self.type = type
        self.color = color
        self.linewidth = linewidth
