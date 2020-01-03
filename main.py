#core
import sys

#files
import read_chunks
import draw



#marching squares algorithm for generating contour data
#TODO:
#clean up with enumeration
#linear interpolation
#line assembly and smoothing
def marching_squares(heightmap):
    data = []
    for y in range(len(heightmap) - 1):
        current_row = []

        for x in range(len(heightmap[0])- 1):
            current_element = []

            #find height values of 2x2 matrix in clockwise order
            case = (
                heightmap[y]    [x]    ,
                heightmap[y]    [x + 1],
                heightmap[y + 1][x + 1],
                heightmap[y + 1][x]
            )

            #return true if height threshold is met
            bitmap = tuple(map(lambda e: e == heightmap[y][x], case))

            #convert point differences to locations for drawing
            if bitmap[0] != bitmap[1]: current_element.append("top")
            if bitmap[1] != bitmap[2]: current_element.append("right")
            if bitmap[2] != bitmap[3]: current_element.append("bottom")
            if bitmap[3] != bitmap[0]: current_element.append("left")

            current_row.append(current_element)

        data.append(current_row)

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

    heightmap = read_chunks.generate_heightmap(world, *args)
    data = marching_squares(heightmap)
    max_len = max(len(data) + 1, len(data[0]) + 1)
    draw.draw(data,
        (
            int(16 / max_len * 30)
        ))

    pass
