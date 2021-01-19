import logging
import sys

from topomc import render
from topomc.common import yaml_open
from topomc.common.logger import Logger
from topomc.parsing.blockmap import Blockmap

from topomc.process import Process
from topomc.symbol import Symbol

from topomc.processes import *
from topomc.symbols import *


def parse_args(args):
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

    return bounding_points, contour_interval, contour_offset, world

def run(args):

    curr_symbol = None

    bounding_points, contour_interval, contour_offset, world = parse_args(args)

    Logger.log(logging.info, "Collecting chunks...")
    blockmap = Blockmap(world, *bounding_points)
    Logger.log(logging.info, "Done", time_it=False)

    Logger.log(logging.info, "STARTING PROCESSES", time_it=False)
    processes = [Process_SC(blockmap) for Process_SC in Process.__subclasses__()]
    for process in processes:
        process.process()
    Logger.log(logging.info, "PROCESSES COMPLETED SUCCESSFULLY", time_it=False)
    
    symbols = [Symbol_SC(processes) for Symbol_SC in Symbol.__subclasses__()]

    Logger.log(logging.info, "RENDER STARTING", time_it=False)
    map_render = render.MapRender(
        len(blockmap.heightmap[0]),
        len(blockmap.heightmap)
    )

    if args.debug:
        curr_symbol = symbols[0] # TODO add support to debug symbols
        map_render.debug(curr_symbol)
    else:
        for symbol in symbols:
            map_render.plot(symbol)
        map_render.show()
    Logger.log(logging.info, "Done", time_it=False)
