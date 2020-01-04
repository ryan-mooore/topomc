#core
import math

#dependencies
try:
    import anvil
except:
    raise Exception("Anvil-parser is not installed or is missing")

#files
import yaml_open

def chunkpos_to_regionpos(chunk):
#convert chunk coords to region coords
    return int(math.floor(chunk / 32))



def load(world, chunkx, chunkz):
    #get region coords from chunk
    (regionx, regionz) = tuple(
        [chunkpos_to_regionpos(chunk_coord) for chunk_coord in (chunkx, chunkz)]
    )

    #get saves path
    saves_path = yaml_open.get("saves_path")

    #path to anvil file
    anvil_file = saves_path \
    + world \
    + "/region/r.{}.{}.mca".format(regionx, regionz)

    #open chunk
    region = anvil.Region.from_file(anvil_file)
    chunk = anvil.Chunk.from_region(region, chunkx, chunkz)

    return chunk