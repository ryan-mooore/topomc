# files
from common import yaml_open
import heightmap as hm
import marching_squares
import draw

MissingCoords = Exception("no co-ordinates for world specified")
InvalidCoords = Exception("Invalid co-ordinates")
InvalidArg = Exception("Contour interval/offset must be an integer")


def run(args):
    try:
        bounding_points = (x1, z1, x2, z2) = [int(x) for x in args[1:5]]
    except ValueError:
        raise MissingCoords
    if x1 > x2 or z1 > z2:
        raise InvalidCoords

    total_bound_chunks = (x2+1 - x1) * (z2+1 - z1)

    try:
        world = args[5]
    except IndexError:
        world = yaml_open.get("world")

    try:
        contour_interval = int(args[6])
    except IndexError:
        contour_interval = yaml_open.get("contour_interval")

    try:
        contour_offset = int(args[7])
    except IndexError:
        contour_offset = yaml_open.get("contour_offset")

    heightmap = hm.create(world, *bounding_points)

    if type(contour_interval) is not int \
            or type(contour_offset) is not int:
        raise InvalidArg

    rendering_data = marching_squares.parse(heightmap, contour_interval)

    scale = yaml_open.get("window_scale")
    draw.draw(rendering_data, scale, total_bound_chunks)
