# marching squares algorithm for generating contour data

class SideHelper:
    def __init__(self, corner1, corner2, x, y):
        self.corner1 = corner1
        self.corner2 = corner2

        self.coords = Coordinates(x, y)



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

        self.isolines = []

class IsolineCoords:
    def __init__(self):
        self.start = Coordinates(0, 0)
        self.end = Coordinates(0, 0)

class Isoline:
    def __init__(self, height):
        self.height = height
        self.coords = IsolineCoords()

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def parse(heightmap, contour_interval=1, contour_offset=0):
    chunk_tile = heightmap.chunk_tiles[0][0]
    print(chunk_tile)
    data = []

    for y in range(len(chunk_tile.heightmap) - 1):
        current_row = []

        for x in range(len(chunk_tile.heightmap[0]) - 1):
            current_element = []

            tmp = chunk_tile.heightmap
            # find height values of 2x2 matrix in clockwise order
            top_left_corner =     tmp[y]    [x]
            top_right_corner =    tmp[y]    [x + 1]
            bottom_right_corner = tmp[y + 1][x + 1]
            bottom_left_corner =  tmp[y + 1][x]

            cell = Cell(
                (
                    top_left_corner,
                    top_right_corner,
                    bottom_right_corner,
                    bottom_left_corner
                ),
                (x, y)
            )

            # algorithm to turn heightmap into isoline co-ordinates
            for lower_height in range(
                cell.min_corner_height,
                cell.max_corner_height):
                upper_height = lower_height + 1

                if (lower_height + contour_offset) % contour_interval == 0:

                    curr_isoline = Isoline(lower_height)

                    search = "start"
                    side_is_endpoint = False

                    for side in cell.sides:
                        # theoretically this loop should only run twice - 
                        # only one height isoline so only one start and end exist

                        if side.corner1 < side.corner2 \
                            and side.corner1 <= lower_height \
                            and side.corner2 >= upper_height: # a height difference exists
                            side_height_difference = \
                                side.corner2 - side.corner1
                            location = (lower_height - side.corner1) \
                                / side_height_difference \
                                + 0.5 / side_height_difference
                            
                            side_is_endpoint = True

                        if side.corner1 > side.corner2 \
                            and side.corner1 >= upper_height \
                            and side.corner2 <=lower_height: # a height difference exists

                            side_height_difference = \
                                side.corner1 - side.corner2
                            location = 1 - (upper_height - side.corner2) \
                                / side_height_difference \
                                + 0.5 / side_height_difference

                            side_is_endpoint = True

                        if side_is_endpoint:
                            coords = Coordinates(side.coords.x, side.coords.y)
                            if coords.x == None:
                                coords.x = location
                            if coords.y == None:
                                coords.y = location

                            if search == "start":
                                curr_isoline.coords.start.x = coords.x
                                curr_isoline.coords.start.y = coords.y
                                search = "end"
                            elif search == "end":
                                curr_isoline.coords.end.x = coords.x
                                curr_isoline.coords.end.y = coords.y

                            side_is_endpoint = False

                    cell.isolines.append(curr_isoline)

            current_row.append(cell)

        data.append(current_row)
    chunk_tile.cells = data
    import pprint
    pp = pprint.PrettyPrinter()
    #pp.pprint(data)

    return heightmap
