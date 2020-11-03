import sys, os
import logging

from common import yaml_open
import heightmap as hm
import pixline
import render
import heightplane

def run(args):
    try:
        bounding_points = x1, z1, x2, z2 = args.x1, args.z1, args.x2, args.z2
    except ValueError:
        logging.critical("App: no co-ordinates for world specified")
        sys.exit()
    if x1 > x2 or z1 > z2:
        logging.critical("App: Invalid co-ordinates")
        sys.exit()

    if args.world:
        logging.info("App: Using explicitly defined world")
        world = args.world
    else:
        world = yaml_open.get("world")

    if args.interval:
        contour_interval = args.interval
        logging.info("App: Using explicitly defined contour interval")
    else:
        contour_interval = yaml_open.get("interval")

    contour_offset = yaml_open.get("phase")

    heightmap = hm.Heightmap(world, *bounding_points)

    if not isinstance(contour_interval, int) \
    or not isinstance(contour_offset, int):
        logging.critical("App: Contour interval/offset must be an integer")

    contours = pixline.march(heightmap, contour_interval)

    render.draw(contours)