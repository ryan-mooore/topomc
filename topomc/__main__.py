import logging
import sys
from argparse import ArgumentParser

import numpy as np
import yaml

from topomc import render
from topomc.common.logger import Logger
from topomc.parsing.blockmap import BlockMap
from topomc.process import Process
from topomc.processes import *
from topomc.symbol import AreaSymbol, LinearSymbol, PointSymbol
from topomc.symbols import *


def main(settings):
    Logger.log(logging.info, "Collecting chunks...")

    blockmap = BlockMap(
        settings["world"],
        *settings["bounding_points"],
        **{k: v for k, v in settings.items() if k in ["surface_blocks", "saves_path"]},
    )

    Logger.log(logging.info, "Preparing to process chunk data...", time_it=False)
    processes = []
    for Process_SC in Process.__subclasses__():
        Logger.log(logging.info, f"Preparing {Process_SC.__name__} process...", sub=1)
        processes.append(
            Process_SC(
                blockmap,
                **{k: v for k, v in settings.items() if k in Process_SC.settings},
            )
        )

    Logger.log(logging.info, "Processing chunk data...", time_it=False)
    for process in processes:
        Logger.log(
            logging.info, f"Running {process.__class__.__name__} process...", sub=1
        )
        process.process()

    height = len(blockmap.heightmap[0])
    width = len(blockmap.heightmap)
    max_len = max(np.floor(width / 16), np.floor(height / 16))

    Logger.log(logging.info, "Creating symbols...")
    symbols = [
        Symbol_SC(processes)
        for Symbol_SC in [
            *AreaSymbol.__subclasses__(),
            *LinearSymbol.__subclasses__(),
            *PointSymbol.__subclasses__(),
        ]
    ]

    Logger.log(logging.info, "Creating render instance...")
    map_render = render.MapRender(
        height,
        width,
        settings["world"],
        **{k: v for k, v in settings.items() if k in render.MapRender.settings},
    )

    if settings["debug"]:
        curr_symbol = symbols[2]  # TODO add support to debug symbols
        map_render.debug(curr_symbol)
    else:
        Logger.log(logging.info, "Rendering symbols...", time_it=False)
        for symbol in symbols:
            Logger.log(
                logging.info, f"Building {symbol.__class__.__name__} symbol...", sub=1
            )
            symbol.render(**{k: v for k, v in settings.items() if k in symbol.settings})

        Logger.log(logging.info, "Rendering map...")
        map_render.show()


def settings_init(args, file="settings.yml"):
    if file:
        try:
            with open(file, "r") as stream:
                settings = yaml.full_load(stream)
        except FileNotFoundError as e:
            Logger.log(logging.critical, f"{file} could not be found")
            raise e
        except Exception as e:
            Logger.log(logging.critical, f"{file} is incorrectly formatted")
    else:
        settings = {}
    for start, end in zip([args.x1, args.z1], [args.x2, args.z2]):
        if end is None or args.debug:
            end = start

    settings = {k.replace(" ", "_").lower(): v for k, v in settings.items()}

    try:
        bounding_points = x1, z1, x2, z2 = args.x1, args.z1, args.x2, args.z2
        settings["bounding_points"] = bounding_points
    except ValueError:
        Logger.log(logging.critical, "No co-ordinates for world specified")
        sys.exit()
    if x1 > x2 or z1 > z2:
        Logger.log(logging.critical, "Invalid co-ordinates")
        sys.exit()

    if args.world:
        settings["world"] = args.world
    else:
        settings["world"] = "New World"
    if args.interval:
        settings["interval"] = args.interval
    settings["debug"] = args.debug

    return settings


def parse_args(args):
    parser = ArgumentParser(description="Generate a map")

    parser.add_argument("x1", type=int, help="X value of start chunk")
    parser.add_argument("z1", type=int, help="Z value of start chunk")
    parser.add_argument(
        "x2", type=int, nargs="?", help="X value of end chunk", default=None
    )
    parser.add_argument(
        "z2", type=int, nargs="?", help="Z value of end chunk", default=None
    )
    parser.add_argument(
        "--debug",
        "-D",
        action="store_true",
        help="Brings up a debug view of selected chunks",
    )
    parser.add_argument(
        "-V", "-v", "--verbose", action="store_true", help="Runs verbose output"
    )
    parser.add_argument(
        "-w",
        "--world",
        metavar="WORLD",
        type=str,
        help="Set world to map",
    )
    parser.add_argument(
        "-I",
        dest="interval",
        metavar="CONTOUR_INT",
        type=int,
        help="Set contour interval",
    )
    parser.add_argument("--settings", type=str, help="Link to settings file")
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(settings_init(args, file=args.settings))
