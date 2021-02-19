import logging
import sys

import yaml

from topomc import render
from topomc.common.logger import Logger
from topomc.parsing.blockmap import BlockMap

from topomc.process import Process
from topomc.symbol import AreaSymbol, LinearSymbol, PointSymbol, Symbol

from topomc.processes import *
from topomc.symbols import *

try:
    with open("settings.yml", "r") as stream:
        settings = yaml.full_load(stream)
except Exception as e:
    Logger.log(logging.critical, f"Settings.yml is incorrectly formatted or missing")
    raise e 

def parse_args(args):
    try:
        bounding_points = x1, z1, x2, z2 = args.x1, args.z1, args.x2, args.z2
        settings["Bounding points"] = bounding_points
    except ValueError:
        Logger.log(logging.critical, "No co-ordinates for world specified")
        sys.exit()
    if x1 > x2 or z1 > z2:
        Logger.log(logging.critical, "Invalid co-ordinates")
        sys.exit()

    if args.world:    settings["World"] = args.world
    if args.interval: settings["Interval"] = args.interval

    return settings

def run(args):

    curr_symbol = None

    settings = parse_args(args)

    Logger.log(logging.info, "Collecting chunks...")
    blockmap = BlockMap(settings["World"], *settings["Bounding points"])

    Logger.log(logging.info, "Preparing to process chunk data...", time_it=False)
    processes = []
    for Process_SC in Process.__subclasses__():
        Logger.log(logging.info, f"Preparing {Process_SC.__name__} process...", sub=1)
        processes.append(Process_SC(blockmap))

    Logger.log(logging.info, "Processing chunk data...", time_it=False)
    for process in processes:
        Logger.log(logging.info, f"Running {process.__class__.__name__} process...", sub=1)
        process.process()
    
    Logger.log(logging.info, "Creating symbols...")
    symbols = [Symbol_SC(processes) for Symbol_SC in 
        AreaSymbol.__subclasses__() +
        LinearSymbol.__subclasses__() +
        PointSymbol.__subclasses__()
    ]

    Logger.log(logging.info, "Creating render instance...")
    map_render = render.MapRender(
        len(blockmap.heightmap[0]),
        len(blockmap.heightmap)
    )

    if args.debug:
        curr_symbol = symbols[2] # TODO add support to debug symbols
        map_render.debug(curr_symbol)
    else:
        Logger.log(logging.info, "Rendering symbols...", time_it=False)
        for symbol in symbols:
            Logger.log(logging.info, f"Building {symbol.__class__.__name__} symbol...", sub=1)
            symbol.render()
        
        Logger.log(logging.info, "Rendering map...")
        map_render.show()
