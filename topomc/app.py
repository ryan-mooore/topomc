#add thickness to contour lines
#object-orient

#core
import sys

#files
from common import yaml_open
import heightmap as hm, marching_squares, draw

def run(args):
    print(args)
    try:
        bounding_points = (x1, z1, x2, z2) = [int(x) for x in args[1:5]]
    except:
        raise Exception("no co-ordinates for world specified")
    if x1 > x2 or z1 > z2:
        raise Exception("Invalid co-ordinates")

    total_bound_chunks = (x2+1 - x1) * (z2+1 - z1)

    try: world = args[5]
    except: world = yaml_open.get("world")

    try: contour_interval = int(args[6])
    except: contour_interval = yaml_open.get("contour_interval")

    try: contour_offset = int(args[7])
    except: contour_offset = yaml_open.get("contour_offset")

    heightmap = hm.create(world, *bounding_points)

    if type(contour_interval) is not int \
    or type(contour_offset)   is not int:
        raise Exception("Contour interval/offset must be an integer")

    rendering_data = marching_squares.parse(heightmap, contour_interval)

    scale = yaml.yaml_open("window_scale")
    draw.draw(rendering_data, scale, total_bound_chunks)
