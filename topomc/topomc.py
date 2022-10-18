import logging
import sys
from argparse import ArgumentParser, Namespace

import yaml

from blockmap import BlockMap
from common.logger import Logger
from PIL import Image
import numpy as np


def main(settings: dict) -> None:
    Logger.log(logging.info, "Importing chunks...", time_it=False)
    blockmap = BlockMap(
        settings["world"],
        *settings["bounding_points"],
        **{k: v for k, v in settings.items() if k in ["surface_blocks", "saves_path"]},
    )

    Logger.log(logging.info, "Processing chunk data...")
    heightmap = np.array(blockmap.heightmap, dtype=np.uint8)
    image = Image.fromarray(heightmap)
    image.save("dem.tif")


def settings_init(args: Namespace, filename: str = "settings.yml") -> dict:
    if filename:
        try:
            with open(filename, "r") as stream:
                settings = yaml.full_load(stream)
                if not settings:
                    settings = {}
        except FileNotFoundError as e:
            Logger.log(logging.critical, f"{filename} could not be found")
            raise e
        except Exception as e:
            Logger.log(logging.critical, f"{filename} is incorrectly formatted")
    else:
        settings = {}
    for start, end in zip([args.x1, args.z1], [args.x2, args.z2]):
        if end is None:
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

    return settings


def parse_args(args: list[str]) -> Namespace:
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
        "-w",
        "--world",
        metavar="WORLD",
        type=str,
        help="Set world to map",
    )
    parser.add_argument("--settings", type=str, help="Link to settings file")

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    main(settings_init(args, filename=args.settings))
