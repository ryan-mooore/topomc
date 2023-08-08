import platform
import sys
from argparse import ArgumentParser, Namespace

import yaml as yaml
from yaml.scanner import ScannerError

from src import convert_world

DEFAULT_SAVES = {
    "windows": "%appdata%\\.minecraft\\saves",
    "darwin": "~/Library/Application Support/minecraft/saves",
    "linux": "~/.minecraft/saves/",
}

surface_blocks = [line.rstrip() for line in open("surface_blocks.txt") if line.rstrip()]
structure_blocks = [line.rstrip() for line in open("structure_blocks.txt") if line.rstrip()]

def settings_init(args: Namespace, filename: str = "settings.yml") -> dict:
    settings = {
        "surface_blocks": surface_blocks,
        "structure_blocks": structure_blocks,
        "saves_path": DEFAULT_SAVES[platform.system().lower()]}
    if filename:
        try:
            with open(filename, "r") as stream:
                advanced_settings = yaml.full_load(stream)
                settings = settings | advanced_settings
        except FileNotFoundError as e:
            print(f"{filename} could not be found")
            sys.exit()
        except ScannerError as e:
            print(f"{filename} is incorrectly formatted")
            sys.exit()
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
    elif not settings["world"]:
        settings["world"] = "New World"
    if args.downsample:
        settings["downsample"] = args.downsample
    elif not settings["downsample"]:
        settings["downsample"] = 1

    if not settings.get("compress_height_limit"):
        settings["compress_height_limit"] = False

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
    parser.add_argument(
        "-d",
        "--downsample",
        metavar="DOWNSAMPLE",
        type=int,
        default=1,
        help="Set downsampling level (default: 1)",
    )
    parser.add_argument("--settings", type=str, help="Link to settings file")
    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_args(sys.argv[1:])
    settings = settings_init(args, filename=args.settings)
    convert_world.to_tiffs(settings)