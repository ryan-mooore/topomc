#core
import sys

#dependencies
import yaml_open

#files
import heightmap
import draw

import json

#marching squares algorithm for generating contour data
#TODO:
#clean up with enumeration
#linear interpolation
#line assembly and smoothing
def marching_squares(heightmap):


    def side_helper(corners, coords):
        self.corners = corners
        self.coords = coords

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

            sides = [
                [(bl, tl), (0, None)],
                [(tl, tr), (None, 1)],
                [(br, tr), (1, None)],
                [(bl, br), (None, 0)]
            ]

            local_height_min = min(tl, tr, bl, br)
            local_height_max = max(tl, tr, bl, br)

            for lower_height in range(local_height_min, local_height_max):
                current_height = []
                upper_height = lower_height + 1

                for side in sides:
                    if side[0][0] < side[0][1]:
                        if side[0][0] <= lower_height and side[0][1] >= upper_height:
                            diff = side[0][1] - side[0][0]
                            location = (lower_height - side[0][0]) / diff + 1 / diff / 2

                            coords = [*side[1]]
                            coords[coords.index(None)] = location
                            current_height.append(coords)


                    elif side[0][0] > side[0][1]:
                        if side[0][0] >= upper_height and side[0][1] <=lower_height:
                            diff = side[0][0] - side[0][1]
                            location = 1 - (upper_height - side[0][1]) / diff + 1 / diff / 2


                            coords = [*side[1]]
                            coords[coords.index(None)] = location
                            current_height.append(coords)

                current_element.append(current_height)

            current_row.append(current_element)

        data.append(current_row)

    print(data)
    jason = json.dumps(data)
    print(jason)
    return data



if __name__ == "__main__":
    try:
        world = sys.argv[1]
    except:
        raise Exception("No world specified")

    try:
        args = [int(x) for x in sys.argv[2:6]]
    except:
        raise Exception("no co-ordinates for world specified")

    heightmap = heightmap.create(world, *args)

    data = marching_squares(heightmap)

    scale = yaml_open.get("window_scale")
    draw.draw(data, scale)

    pass
