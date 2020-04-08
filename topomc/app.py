import sys, os
# files
from common import yaml_open
import heightmap as hm
import marching_squares
import draw
import vectorize
import logging

def run(args):
    try:
        bounding_points = x1, z1, x2, z2 = args.x1, args.z1, args.x2, args.z2
    except ValueError:
        logging.critical("App: no co-ordinates for world specified")
        return 1
    if x1 > x2 or z1 > z2:
        logging.critical("App: Invalid co-ordinates")
        return 1

    if args.world:
        world = args.world
    else:
        logging.info("App: No world found, using default")
        world = yaml_open.get("world")

    if args.interval:
        contour_interval = args.interval
    else:
        logging.info("App: None or invalid contour interval found, using default")
        contour_interval = yaml_open.get("interval")

    contour_offset = yaml_open.get("phase")

    heightmap = hm.Heightmap(world, *bounding_points)

    if not isinstance(contour_interval, int) \
    or not isinstance(contour_offset, int):
        logging.critical("App: Contour interval/offset must be an integer")

    marching_squares.square_march(heightmap, contour_interval)
    if args.debug:
        draw.debug(heightmap)
    else:
        topodata = vectorize.Topodata(heightmap)
        draw.draw(topodata)