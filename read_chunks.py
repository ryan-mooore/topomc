#core
import math

#dependencies
try:
    import anvil
except:
    raise Exception("Anvil-parser is not installed or is missing")

try:
    import yaml
except:
    raise Exception("Yaml is not installed or is missing")



#get path to minecraft save folder
def get_saves_path():
    try:
        with open("path_to_saves.txt", "r") as path_file:
            saves_path = path_file.readline()
            path_file.close()

        return saves_path

    except:
        raise Exception("path_to_saves.txt not found")



def get_surface_blocks():
    with open("block_settings.yaml", "r") as block_settings:
        block_settings = yaml.full_load(block_settings)
        return block_settings["surface_blocks"]



def chunk_to_reg(chunk):
#convert chunk coords to region coords
    return int(math.floor(chunk / 32))



#generate 2d heightmap matrix
def get_chunk_height(world, chunkx, chunkz):
    #get region coords from chunk
    (regionx, regionz) = tuple(
        [chunk_to_reg(chunk_coord) for chunk_coord in (chunkx, chunkz)]
    )

    #get saves path and surface blocks
    saves_path = get_saves_path()
    surface_blocks = get_surface_blocks()

    #path to anvil file
    anvil_file = saves_path \
    + world \
    + "/region/r.{}.{}.mca".format(regionx, regionz)

    #open chunk
    region = anvil.Region.from_file(anvil_file)
    chunk = anvil.Chunk.from_region(region, chunkx, chunkz)

    #generate heightmap
    heightmap = []

    for z in range (16):
        current_row = []

        for x in range (16):
            for y in range(0xFF, 0, -1):
                block = chunk.get_block(x, y, z).id

                if block in surface_blocks:
                    current_row.append(y)
                    break

        heightmap.append(current_row)

    return heightmap



#append one chunk to row
def horizontal_append(map1, map2):
    #append if map contains content
    if map1:
        for index, row in enumerate(map2):
            map1[index].extend(row)

    #create content
    else:
        map1 = map2

    return map1



def vertical_append(map1, map2):
    #append if map contains content
    if map1:
        for row in map2:
            map1.append(row)

    #create content
    else:
        map1 = map2

    return map1



def generate_heightmap(world, chunkx1, chunkz1, chunkx2, chunkz2):
    heightmap = []

    # + 1 because ending chunks are inclusive
    for z in range(chunkz1, chunkz2 + 1):
        chunk_row = []

        for x in range(chunkx1, chunkx2 + 1):
            chunk = get_chunk_height(world, x, z)
            chunk_row = horizontal_append(chunk_row, chunk)

        heightmap = vertical_append(heightmap, chunk_row)

    return heightmap