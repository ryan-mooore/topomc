import subprocess
import sys
import webbrowser
from argparse import ArgumentParser, Namespace
from os import path

import yaml as yaml

from topomc import convert_world

SURFACE_BLOCKS = [
    "grass_block",
    "grass_path",
    "dirt",
    "coarse_dirt",
    "farmland",
    "sand",
    "sandstone",
    "red_sand",
    "red_sandstone",
    "clay",
    "podzol",
    "mycelium",
    "stone",
    "granite",
    "diorite",
    "andesite",
    "gravel",
    "coal_ore",
    "iron_ore",
    "gold_ore",
    "water",
]


def settings_init(args: Namespace, filename: str = "settings.yml") -> dict:
    settings = {"surface_blocks": SURFACE_BLOCKS}
    if filename:
        try:
            with open(filename, "r") as stream:
                settings = settings | yaml.full_load(stream)
        except FileNotFoundError as e:
            print(f"{filename} could not be found")
            raise e
        except Exception as e:
            print(f"{filename} is incorrectly formatted")
    for start, end in zip([args.x1, args.z1], [args.x2, args.z2]):
        if end is None:
            end = start

    settings = {k.replace(" ", "_").lower(): v for k, v in settings.items()}

    try:
        bounding_points = x1, z1, x2, z2 = args.x1, args.z1, args.x2, args.z2
        settings["bounding_points"] = bounding_points
    except ValueError:
        print("No co-ordinates for world specified")
        sys.exit()
    if x1 > x2 or z1 > z2:
        print("Invalid co-ordinates")
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
    settings = settings_init(args, filename=args.settings)
    convert_world.to_tiffs(settings)
    subprocess.run("Rscript topomc/create_map.R", shell=True)
    webbrowser.open("file://" + path.realpath("map.html"))