from __future__ import annotations

from typing import Any, Union

T = Union[float, int]


class Coordinates:
    __slots__ = ["x", "y"]

    def __init__(self, x: T, y: T) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"(x={self.x}, y={self.y})"

    @staticmethod
    def to_list(iist: list[Coordinates]) -> tuple[list[T], list[T]]:
        return [vertice.x for vertice in iist], [vertice.y for vertice in iist]

    @staticmethod
    def from_list(xlist: list[T], ylist: list[T]) -> list[Coordinates]:
        return [Coordinates(x, y) for x, y in zip(xlist, ylist)]

    def to_tuple(self) -> tuple[T, T]:
        return (self.x, self.y)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Coordinates):
            return NotImplemented

        return self.x == other.x and self.y == other.y
