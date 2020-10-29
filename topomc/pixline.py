# marching squares algorithm for generating contour data
from common import progressbar

class SideHelper:
    def __init__(self, corner1, corner2, x, y):
        self.corner1 = corner1
        self.corner2 = corner2

        self.coords = Coordinates(x, y)

    @property
    def direction(self):
        if self.corner1 < self.corner2:
            return 1
        elif self.corner1 > self.corner2:
            return -1
        else:
            return None

    @property
    def difference(self):
        if self.direction == 1:
            return self.corner2 - self.corner1
        elif self.direction == -1:
            return self.corner1 - self.corner2
        else:
            return 0

class Cell:
    def __init__(self, sides, coords):
        (tl, tr, br, bl) = sides
        self.sides = (
            SideHelper(bl, tl, 0, None),
            SideHelper(tl, tr, None, 1),
            SideHelper(br, tr, 1, None),
            SideHelper(bl, br, None, 0)
        )
        self.coords = Coordinates(*coords)

        self.min_corner_height = min(tl, tr, bl, br)
        self.max_corner_height = max(tl, tr, bl, br)

        self.pixlines = []

class PixlineCoords:
    def __init__(self):
        self.start = Coordinates(0, 0)
        self.end = Coordinates(0, 0)
    
    @property
    def x(self):
        return self.start.x, self.end.x
    @x.setter
    def x(self, value):
        self.start.x, self.end.x = value
    
    @property
    def y(self):
        return self.start.y, self.end.y
    @y.setter
    def y(self, value):
        self.start.y, self.end.y = value

    def x_diff(self):
        return self.end.x - self.start.x
    def y_diff(self):
        return self.end.y - self.start.y

class Pixline:
    def __init__(self, height, direction):
        self.height = height
        self.coords = PixlineCoords()
        self.direction = direction

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
    """
    for chunk_tile_row in heightmap.chunk_tiles:
        for chunk_tile in chunk_tile_row:"""

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

            # algorithm to turn heightmap into pixline co-ordinates
            for lower_height in range(
                cell.min_corner_height,
                cell.max_corner_height):
                upper_height = lower_height + 1

                if (lower_height + contour_offset) % contour_interval == 0:

                    search = "start"
                    side_is_endpoint = False

                    for side in cell.sides:
                        # theoretically this loop should only run twice -
                        # only one height pixline so only one start and end exist

                        if side.direction == 1 \
                            and side.corner1 <= lower_height \
                            and side.corner2 >= upper_height: # a height difference exists

                            location = (lower_height - side.corner1) \
                                / side.difference + 0.5 / side.difference
                            
                            if search == "start":
                                direction = 1

                            side_is_endpoint = True

                        if side.direction == -1 \
                            and side.corner1 >= upper_height \
                            and side.corner2 <=lower_height: # a height difference exists

                            location = 1 - (upper_height - side.corner2) \
                                / side.difference + 0.5 / side.difference
                            
                            if search == "start":
                                direction = -1

                            side_is_endpoint = True

                        if side_is_endpoint:
                            coords = Coordinates(side.coords.x, side.coords.y)
                            if coords.x == None:
                                coords.x = location
                            if coords.y == None:
                                coords.y = location

                            if search == "start":
                                pixline = Pixline(lower_height, direction)
                                pixline.coords.start.x = coords.x
                                pixline.coords.start.y = coords.y
                                search = "end"
                            elif search == "end":
                                pixline.coords.end.x = coords.x
                                pixline.coords.end.y = coords.y
                                pixline.direction = 1
                                cell.pixlines.append(pixline)
                                search = "start"

                            side_is_endpoint = False
            cells_created += 1
            if cells_created % 50 == 0 or cells_created == cells_to_create:
                progressbar._print(
                    cells_created,
                    cells_to_create,
                    2,
                    "pixline cells created"
                )
            
            cell_row.append(cell)

        heightmap.cells.append(cell_row)
