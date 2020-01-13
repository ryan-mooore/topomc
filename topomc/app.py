#add thickness to contour lines
#object-orient

#core
import sys

#files
from common import yaml
import heightmap as hm, marching_squares, draw

def run():
    try:
        bounding_points = (x1, z1, x2, z2) = [int(x) for x in sys.argv[1:5]]
    except:
        raise Exception("no co-ordinates for world specified")
    if x1 > x2 or z1 > z2:
        raise Exception("Invalid co-ordinates")

    total_bound_chunks = (x2+1 - x1) * (z2+1 - z1)

    try: world = sys.argv[5]
    except: world = yaml.yaml_open("world")

    try: contour_interval = int(sys.argv[6])
    except: contour_interval = yaml.yaml_open("contour_interval")

    try: contour_offset = int(sys.argv[7])
    except: contour_offset = yaml.yaml_open("contour_offset")

    heightmap = hm.create(world, *bounding_points)

    if type(contour_interval) is not int \
    or type(contour_offset)   is not int:
        raise Exception("Contour interval/offset must be an integer")

    rendering_data = marching_squares.parse(heightmap, contour_interval)

    scale = yaml.yaml_open("window_scale")
    draw.draw(rendering_data, scale, total_bound_chunks)
