#add thickness to contour lines
#object-orient



#core
import sys

#files
from res import yaml_open
import heightmap
import marching_squares
import draw



if __name__ == "__main__":
    try:
        bounding_points = (x1, y1, x2, y2) = [int(x) for x in sys.argv[1:5]]
    except:
        raise Exception("no co-ordinates for world specified")
    if x1 > x2 or y1 > y2:
        raise Exception("Invalid co-ordinates")

    total_bound_chunks = (x2+1 - x1) * (y2+1 - y1)

    try: world = sys.argv[5]
    except: world = yaml_open("world")

    try: contour_interval = int(sys.argv[6])
    except: contour_interval = yaml_open("contour_interval")

    try: contour_offset = int(sys.argv[7])
    except: contour_offset = yaml_open("contour_offset")

    heightmap = heightmap.create(world, *bounding_points, total_bound_chunks)

    if type(contour_interval) is not int \
    or type(contour_offset)   is not int:
        raise Exception("Contour interval/offset must be an integer")

    rendering_data = marching_squares.marching_squares(heightmap, contour_interval)

    scale = yaml_open("window_scale")
    draw.draw(rendering_data, scale, total_bound_chunks)

    pass
