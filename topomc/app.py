# files
from common import yaml_open
import heightmap as hm
import marching_squares
import draw
import vectorize

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

    heightmap = hm.Heightmap(world, *bounding_points)

    if not isinstance(contour_interval, int) \
    or not isinstance(contour_offset, int):
        raise InvalidArg

    squaremarch = marching_squares.SquareMarch(heightmap, contour_interval)

    topodata = vectorize.Topodata(squaremarch)
    scale = yaml_open.get("window_scale")
    draw.draw(topodata, scale, total_bound_chunks)
