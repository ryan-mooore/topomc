# marching squares algorithm for generating contour data
from common import progressbar
from enum import Enum

class EdgeType(Enum):
    LEFT = "left"
    TOP = "top"
    BOTTOM = "bottom"
    RIGHT = "right"

class Edge:
    def __init__(self, corner1, corner2, x, y, edgetype):
        self.corner1 = corner1
        self.corner2 = corner2

        self.coords = Coordinates(x, y)

        self.type = edgetype

    def flip_edge(self) -> EdgeType:
        
        mapper = {
            EdgeType.TOP: EdgeType.BOTTOM,
            EdgeType.BOTTOM: EdgeType.TOP,
            EdgeType.LEFT: EdgeType.RIGHT,
            EdgeType.RIGHT: EdgeType.LEFT
        }

        return mapper[self.type]

    @property
    def direction(self):
        if self.corner1 < self.corner2:
            return 1
        elif self.corner1 > self.corner2:
            return -1
        else:
            return None

    def min_corner(self): return min(self.corner1, self.corner2)
    def max_corner(self): return max(self.corner1, self.corner2)

    @property
    def difference(self):
        if self.direction == 1:
            return self.corner2 - self.corner1
        elif self.direction == -1:
            return self.corner1 - self.corner2
        else:
            return 0

class Cell:
    def __init__(self, edges, coords):
        (tl, tr, br, bl) = edges
        self.edges = {
            EdgeType.LEFT:   Edge(bl, tl, 0, None, EdgeType.LEFT),
            EdgeType.TOP:    Edge(tl, tr, None, 1, EdgeType.TOP),
            EdgeType.RIGHT:  Edge(br, tr, 1, None, EdgeType.RIGHT),
            EdgeType.BOTTOM: Edge(bl, br, None, 0, EdgeType.BOTTOM)
        }
        self.coords = Coordinates(*coords)

        self.min_corner_height = min(tl, tr, bl, br)
        self.max_corner_height = max(tl, tr, bl, br)

        self.contours = {}
        for possible_height in range(self.min_corner_height, self.max_corner_height + 1):
            self.contours[possible_height] = None

class Isoline:
    def __init__(self):
        self.contour = []
        self.direction = 0
        self.closed = False

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Coordinates):
            return NotImplemented

        return self.x == other.x and self.y == other.y

    def get_list(self):
        return self.x, self.y

    def __repr__(self):
        return f"{self.x, self.y}"

def march(heightmap, contour_interval=1, contour_offset=0):

    heightmap.contours = []

    heightmap.cells = []
    cells_created = 0
    cells_to_create = (len(heightmap.heightmap) - 1) * (len(heightmap.heightmap[0]) - 1)

    for z in range(len(heightmap.heightmap) - 1):
        cell_row = []
        for x in range(len(heightmap.heightmap[0]) - 1):
            hm = heightmap.heightmap
            # find height values of 2x2 matrix in clockwise order
            top_left_corner =     hm[z]    [x]
            top_right_corner =    hm[z]    [x + 1]
            bottom_right_corner = hm[z + 1][x + 1]
            bottom_left_corner =  hm[z + 1][x]

            cell = Cell(
                (
                    top_left_corner,
                    top_right_corner,
                    bottom_right_corner,
                    bottom_left_corner
                ),
                (x, z)
            )

            cell_row.append(cell)

        heightmap.cells.append(cell_row)

# cells created

    def hop_to_next_cell(cell: Cell, edge: Edge) -> Cell:
        if edge.type == EdgeType.TOP:    return heightmap.cells[cell.coords.y - 1][cell.coords.x]
        if edge.type == EdgeType.RIGHT:  return heightmap.cells[cell.coords.y][cell.coords.x + 1]
        if edge.type == EdgeType.LEFT:   return heightmap.cells[cell.coords.y][cell.coords.x - 1]
        if edge.type == EdgeType.BOTTOM: return heightmap.cells[cell.coords.y + 1][cell.coords.x]

        print(f"Error: no contour found: Heigh")

    def has_hit_boundary(cell: Cell, edge: Edge) -> bool:
        
        et = edge.type
        pos = cell.coords

        if \
        et == EdgeType.LEFT   and pos.x == 0 or \
        et == EdgeType.TOP    and pos.y == 0 or \
        et == EdgeType.RIGHT  and pos.x == len(heightmap.cells[0]) - 1 or \
        et == EdgeType.BOTTOM and pos.y == len(heightmap.cells)    - 1:
            return True
        else: 
            return False

    def create_point_coords(edge: Edge, point: float) -> Coordinates:
        coords = Coordinates(edge.coords.x, edge.coords.y)

        if coords.x == None:
            coords.x = point
        if coords.y == None:
            coords.y = point
        
        return coords

    def has_self_closed(isoline):
        if isoline.closed:
            if len(isoline.contour) > 3:
                if isoline.contour[1] == isoline.contour[-1]:
                    return True
                else:
                    return False

    def trace_from_here(cell, edge, height, closed=False) -> Isoline:
        if edge.min_corner() <= height < edge.max_corner(): # a contour starts at this edge at this height
            
            isoline = Isoline()
            if closed:
                isoline.closed = True
            else:
                distance_from_edge = height - edge.min_corner()

                point = distance_from_edge / edge.difference
                if edge.direction == -1: point = 1 - point

                cell.contours[height] = isoline
                point_coords = create_point_coords(edge, point)
                isoline.contour.append((point_coords, cell.coords))
            
            edge = cell.edges[edge.flip_edge()]

            while True:
                possible_edges = [*cell.edges]
                possible_edges.remove(edge.flip_edge()) # remove edge contour came from
                for edge_type in possible_edges:
                    
                    edge = cell.edges[edge_type]
                    if edge.min_corner() <= height < edge.max_corner(): # a contour starts at this edge at this height
                        
                        cell.contours[height] = isoline
                        distance_from_edge = height - edge.min_corner()
                        point = distance_from_edge / edge.difference
                        if edge.direction == -1: point = 1 - point
                        point_coords = create_point_coords(edge, point)
                        isoline.contour.append((point_coords, cell.coords))

                        if has_hit_boundary(cell, edge):
                            return isoline
                        
                        elif has_self_closed(isoline):
                            return isoline

                        else:
                            cell = hop_to_next_cell(cell, edge)
                            break
                else:
                    print("error")
                    break
    
    def start_traces(cell: Cell, edgetype: EdgeType) -> None:
        for height, referenced in cell.contours.items():
            if height in cell.contours:
                if not referenced:
                    isoline = trace_from_here(cell, cell.edges[edgetype], height)
                    if isoline:
                        heightmap.contours.append(isoline)

    for cell in heightmap.cells[0]: 
        start_traces(cell, EdgeType.TOP)
    for row in heightmap.cells: 
        start_traces(row[len(row) - 1], EdgeType.RIGHT)
    for cell in heightmap.cells[len(heightmap.cells) - 1]: 
        start_traces(cell, EdgeType.BOTTOM)
    for row in heightmap.cells: 
        start_traces(row[0], EdgeType.LEFT)

    for row in heightmap.cells:
        for cell in row:
            for height, referenced in cell.contours.items():
                if not referenced:
                    for edge in cell.edges.values():
                        if edge.min_corner() <= height < edge.max_corner():
                            isoline = trace_from_here(cell, edge, height, closed=True)
                            if isoline:
                                heightmap.contours.append(isoline)
                            break

    return heightmap



