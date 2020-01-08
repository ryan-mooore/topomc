#marching squares algorithm for generating contour data
#TODO:
#clean up with enumeration
#linear interpolation
#line assembly and smoothing

def marching_squares(heightmap):

    class SideHelper:
        def __init__(self, corner1, corner2, x, y):
            self.corner1 = corner1
            self.corner2 = corner2

            self.x = x
            self.y = y

    data = []
    for y in range(len(heightmap) - 1):
        current_row = []

        for x in range(len(heightmap[0])- 1):
            current_element = []

            #find height values of 2x2 matrix in clockwise order
            tl = heightmap[y]    [x]
            tr = heightmap[y]    [x + 1]
            br = heightmap[y + 1][x + 1]
            bl = heightmap[y + 1][x]

            class Cell:

                sides = [
                    SideHelper(bl, tl, 0, None),
                    SideHelper(tl, tr, None, 1),
                    SideHelper(br, tr, 1, None),
                    SideHelper(bl, br, None, 0)
                ]

            cell = Cell()

            local_height_min = min(tl, tr, bl, br)
            local_height_max = max(tl, tr, bl, br)

            for lower_height in range(local_height_min, local_height_max):
                current_height = []
                upper_height = lower_height + 1

                for side in cell.sides:
                    if side.corner1 < side.corner2:
                        if side.corner1 <= lower_height and side.corner2 >= upper_height:
                            diff = side.corner2 - side.corner1
                            location = (lower_height - side.corner1) / diff + 1 / diff / 2

                            coords = [side.x, side.y]
                            coords[coords.index(None)] = location
                            current_height.append(coords)


                    elif side.corner1 > side.corner2:
                        if side.corner1 >= upper_height and side.corner2 <=lower_height:
                            diff = side.corner1 - side.corner2
                            location = 1 - (upper_height - side.corner2) / diff + 1 / diff / 2


                            coords = [side.x, side.y]
                            coords[coords.index(None)] = location
                            current_height.append(coords)

                current_element.append(current_height)

            current_row.append(current_element)

        data.append(current_row)

    return data
