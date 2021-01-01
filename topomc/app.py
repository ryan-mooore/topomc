import sys
import logging
from topomc.symbols.contour import Contour

from topomc.common import yaml_open
from topomc.common.logger import Logger
from topomc.parsing import heightmap
from topomc import render

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

    if not isinstance(contour_interval, int) \
    or not isinstance(contour_offset, int):
        logging.critical("App: Contour interval/offset must be an integer")



    Logger.log(logging.info, "Collecting chunks...")
    hmap = heightmap.Heightmap(world, *bounding_points)
    Logger.log(logging.info, "Done", t=False)

    symbols = []
    contour = Contour()
    symbols.append(contour)

    Logger.log(logging.info, "BUILD STARTING", t=False)
    for symbol in symbols:
        symbol.build(hmap)
    Logger.log(logging.info, "BUILD COMPLETED SUCCESSFULLY", t=False)

    Logger.log(logging.info, "RENDER STARTING")
    map_render = render.MapRender(len(hmap.heightmap[0]), len(hmap.heightmap))
    if args.debug: map_render.debug(symbols)
    else:          map_render.render(symbols)
    Logger.log(logging.info, "Done", t=False)
