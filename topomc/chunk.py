# core
import math
import os

# dependencies
try:
    import anvil
except ImportError:
    raise Exception("Anvil-parser is not installed or is missing")

# files
from common import yaml_open


def chunkpos_to_regionpos(chunk):
    '''convert chunk coords to region coords'''
    return int(math.floor(chunk / 32))


def load(world, chunkx, chunkz):
    '''returns chunk object from coords'''
    (regionx, regionz) = tuple([
        chunkpos_to_regionpos(chunk_coord) for chunk_coord in (chunkx, chunkz)
    ])

    saves_path = yaml_open.get("saves_path")
    world_path = saves_path + world

    # test to see whether world exists
    if not os.path.isdir(world_path):
        print()
        print("Available worlds:")
        for world in os.listdir(saves_path):
            if not world[2:-2].endswith("UNDO"):
                print(world)

        raise Exception("World does not exist!")

    anvil_file = world_path + "/region/r.{}.{}.mca".format(regionx, regionz)

    # open chunk
    try:
        region = anvil.Region.from_file(anvil_file)
    except Exception:
        raise Exception("Unloaded chunk(s)!")

    chunk = anvil.Chunk.from_region(region, chunkx, chunkz)

    return chunk
