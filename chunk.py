#core
import math
import os, sys

#dependencies
try:
    import anvil
except:
    raise Exception("Anvil-parser is not installed or is missing")

#files
from res import yaml_open



def chunkpos_to_regionpos(chunk):
#convert chunk coords to region coords
    return int(math.floor(chunk / 32))



def load(world, chunkx, chunkz):
    #get region coords from chunk
    (regionx, regionz) = tuple(
        [chunkpos_to_regionpos(chunk_coord) for chunk_coord in (chunkx, chunkz)]
    )

    #get saves path
    saves_path = yaml_open("saves_path")

    if sys.platform.startswith('win32') \
    or sys.platform.startswith('cygwin'):
        path_slash = '\\'
    else:
        path_slash = '/'

    #path to world
    region_path = f"{saves_path}{world}{path_slash}region{path_slash}"

    #test to see whether world exists
    if not os.path.isdir(region_path):
        raise Exception("World does not exist or error retrieving path")

    anvil_file = region_path + f"r.{regionx}.{regionz}.mca"

    #open chunk
    try:
        region = anvil.Region.from_file(anvil_file)
    except:
        raise Exception("Unloaded chunk(s)!")

    chunk = anvil.Chunk.from_region(region, chunkx, chunkz)

    return chunk
