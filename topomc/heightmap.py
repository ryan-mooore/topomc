from common import bin, progressbar, yaml_open
import chunk

# builtin chunk heightmap options
tags = [
    "OCEAN_FLOOR",
    "MOTION_BLOCKING_NO_LEAVES",
    "MOTION_BLOCKING",
    "WORLD_SURFACE"
]

# game consts
INDEX_OF_HEIGHTMAPS = 6
STREAM_BITS_PER_VALUE = 9
STREAM_INT_SIZE = 64

class Chunk:
    def get_extremes(self):
        min_height = 0xFF
        max_height = 0x00
        for row in self.hm:
            for point_height in row:
                if point_height < min_height: min_height = point_height
                if point_height > max_height: max_height = point_height
        
        return (min_height, max_height)
                

class Heightmap:
    def __init__(self, chunks):
        self.chunks = chunks


def get_hm_data(anvil, tag="MOTION_BLOCKING_NO_LEAVES"):
    try:
        tags.index(tag)
    except Exception:
        raise Exception("Invalid tag")

    INDEX_OF_TAG = tags.index(tag)
    
    try:
        hm_data_stream = \
            anvil.tags[INDEX_OF_HEIGHTMAPS].tags[INDEX_OF_TAG]
    except Exception:
        raise Exception("Unloaded chunk(s)!")

    hm_data = bin.unstream(
        hm_data_stream, STREAM_BITS_PER_VALUE, STREAM_INT_SIZE
    )


    hm_data_formatted = []
    current_row = []
    for index, point_height in enumerate(hm_data):
        if index % 16 == 0:
            if current_row:
                hm_data_formatted.append(current_row)
            current_row = []
        current_row.append(point_height)
    hm_data_formatted.append(current_row)

    return hm_data_formatted

# generate 2d heightmap matrix
def create_chunk(world, chunkx, chunkz):

    curr_chunk = Chunk()
    curr_chunk.anvil = chunk.load(world, chunkx, chunkz)
    curr_chunk.hmdata = get_hm_data(curr_chunk.anvil.data, tags[1])

    surface_blocks = yaml_open.get("surface_blocks")

    # generate heightmap
    heightmap = []

    for z in range(16):
        current_row = []

        for x in range(16):
            start = curr_chunk.hmdata[z][x] - 1
            for y in range(start, 0, -1):
                block = curr_chunk.anvil.get_block(x, y, z).id

                if block in surface_blocks:
                    current_row.append(y)
                    break

        heightmap.append(current_row)

    curr_chunk.hm = heightmap
    return curr_chunk


def create(world, chunkx1, chunkz1, chunkx2, chunkz2):

    chunks_to_retrieve = (chunkx2+1 - chunkx1) * (chunkz2+1 - chunkz1)

    heightmap = []
    chunks_retrieved = 0

    # + 1 because ending chunks are inclusive
    for z in range(chunkz1, chunkz2 + 1):
        chunk_row = []

        for x in range(chunkx1, chunkx2 + 1):
            chunk_row.append(create_chunk(world, x, z))

            chunks_retrieved += 1
            progressbar._print(
                chunks_retrieved,
                chunks_to_retrieve,
                1,
                "chunks retrieved"
            )

        heightmap.append(chunk_row)

    return Heightmap(heightmap)
