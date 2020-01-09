#marching squares algorithm for generating contour data
#TODO:
#clean up with enumeration
#linear interpolation
#line assembly and smoothing



class SideHelper:
    def __init__(self, corner1, corner2, x, y):
        self.corner1 = corner1
        self.corner2 = corner2

        self.x = x
        self.y = y



class Cell:

    def __init__(self, tl, tr, br, bl):
        self.sides = [
            SideHelper(bl, tl, 0, None),
            SideHelper(tl, tr, None, 1),
            SideHelper(br, tr, 1, None),
            SideHelper(bl, br, None, 0)
        ]

        self.min_corner_height = min(tl, tr, bl, br)
        self.max_corner_height = max(tl, tr, bl, br)



def marching_squares(heightmap, contour_interval = 1, contour_offset = 0):

    data = []

    for y in range(len(heightmap) - 1):
        current_row = []

        for x in range(len(heightmap[0])- 1):
            current_element = []

            #find height values of 2x2 matrix in clockwise order
            top_left_corner =     heightmap[y]    [x]
            top_right_corner =    heightmap[y]    [x + 1]
            bottom_right_corner = heightmap[y + 1][x + 1]
            bottom_left_corner =  heightmap[y + 1][x]

            cell = Cell(
                top_left_corner,
                top_right_corner,
                bottom_right_corner,
                bottom_left_corner
            )

            #algorithm to turn heightmap into isoline co-ordinates
            for lower_height in range(cell.min_corner_height, cell.max_corner_height):
                upper_height = lower_height + 1

                cell_coord_data = []

                if (lower_height + contour_offset) % contour_interval == 0:

                    for side in cell.sides:

                        if side.corner1 < side.corner2 \
                            and side.corner1 <= lower_height \
                            and side.corner2 >= upper_height:

                            side_height_difference = side.corner2 - side.corner1
                            location = (lower_height - side.corner1) \
                                / side_height_difference \
                                + 0.5 / side_height_difference

                            coords = [side.x, side.y]
                            coords[coords.index(None)] = location
                            cell_coord_data.append(coords)

                        if side.corner1 > side.corner2 \
                            and side.corner1 >= upper_height \
                            and side.corner2 <=lower_height:

                            side_height_difference = side.corner1 - side.corner2
                            location = 1 - (upper_height - side.corner2) \
                                / side_height_difference \
                                + 0.5 / side_height_difference

                            coords = [side.x, side.y]
                            coords[coords.index(None)] = location
                            cell_coord_data.append(coords)

                current_element.append(cell_coord_data)

            current_row.append(current_element)

        data.append(current_row)

    return data
