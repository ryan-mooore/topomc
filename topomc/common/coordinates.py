class Coordinates:
    __slots__ = ["x", "y"]

    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
    
    def __repr__(self) -> str:
        return f"(x={self.x}, y={self.y})"

    @staticmethod
    def transpose_list(iist):
        return [vertice.x for vertice in iist], [vertice.y for vertice in iist]

    def to_tuple(self):
        return (self.x, self.y)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Coordinates):
            return NotImplemented

        return self.x == other.x and self.y == other.y
