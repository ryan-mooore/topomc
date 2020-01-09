#files
import unstream
import chunk
import yaml_open

def get_from_chunk(world, chunkx, chunkz, tag = "MOTION_BLOCKING_NO_LEAVES"):
    #builtin chunk heightmap options
    tags = [
        "OCEAN_FLOOR",
        "MOTION_BLOCKING_NO_LEAVES",
        "MOTION_BLOCKING",
        "WORLD_SURFACE"
    ]

    #check for valid tag
    try:
        tags.index(tag)
    except:
        raise Exception("Invalid tag")

    #game consts
    INDEX_OF_HEIGHTMAPS = 6
    INDEX_OF_TAG = tags.index(tag)
    STREAM_BITS_PER_VALUE = 9
    STREAM_INT_SIZE = 64

    #load chunk
    current_chunk = chunk.load(world, chunkx, chunkz)

    #get heightmap data

    try:
        hm_data_stream = current_chunk.data.tags[INDEX_OF_HEIGHTMAPS].tags[INDEX_OF_TAG]
    except:
        raise Exception("Unloaded chunk(s)!")

    hm_data = unstream.unstream(
        hm_data_stream, STREAM_BITS_PER_VALUE, STREAM_INT_SIZE
    )

    heightmap = []
    current_row = []
    for index, point_height in enumerate(hm_data):
        if index % 16 == 0:
            if current_row:
                heightmap.append(current_row)
            current_row = []
        current_row.append(point_height)
    heightmap.append(current_row)
    return heightmap



#generate 2d heightmap matrix
def create_from_chunk(world, chunkx, chunkz):

    current_chunk = chunk.load(world, chunkx, chunkz)

    surface_blocks = yaml_open.get("surface_blocks")

    builtin_hm = get_from_chunk(world, chunkx, chunkz, "MOTION_BLOCKING_NO_LEAVES")

    #generate heightmap
    heightmap = []

    for z in range (16):
        current_row = []

        for x in range (16):
            start = builtin_hm[z][x]

            for y in range(start, 0, -1):
                block = current_chunk.get_block(x, y, z).id

                if block in surface_blocks:
                    current_row.append(y)
                    break

        heightmap.append(current_row)


    return heightmap



def create(world, chunkx1, chunkz1, chunkx2, chunkz2, chunks_to_retrieve):

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

    heightmap = []
    chunks_retrieved = 0

    # + 1 because ending chunks are inclusive
    for z in range(chunkz1, chunkz2 + 1):
        chunk_row = []

        for x in range(chunkx1, chunkx2 + 1):
            current_chunk = create_from_chunk(world, x, z)
            chunk_row = horizontal_append(chunk_row, current_chunk)

            chunks_retrieved += 1
            print("{}/{} chunks retrieved".format(
                chunks_retrieved, chunks_to_retrieve
            ))

        heightmap = vertical_append(heightmap, chunk_row)

    return heightmap