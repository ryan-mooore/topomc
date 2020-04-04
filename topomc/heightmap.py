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

class ChunkTile:
    def get_extremes(self):
        min_height = 0xFF
        max_height = 0x00

        point_heights = [point_height for row in self.heightmap for point_height in row]
        min_height = min(*point_heights)
        max_height = max(*point_heights)
        
        return (min_height, max_height)
                

class Heightmap:
    def __init__(self, chunk_tiles):
        self.chunk_tiles = chunk_tiles


def get_chunktag_heightmap(anvil, tag="MOTION_BLOCKING_NO_LEAVES"):
    try:
        tags.index(tag)
    except Exception:
        raise Exception("Invalid tag")

    INDEX_OF_TAG = tags.index(tag)
    
    try:
        data_stream = \
            anvil.tags[INDEX_OF_HEIGHTMAPS].tags[INDEX_OF_TAG]
    except Exception:
        raise Exception("Unloaded chunk(s)!")

    chunktag_heightmap = bin.unstream(
        data_stream, STREAM_BITS_PER_VALUE, STREAM_INT_SIZE
    )

    chunktag_heightmap_deepened = []
    row = []
    for index, point_height in enumerate(chunktag_heightmap):
        if index % 16 == 0:
            if row:
                chunktag_heightmap_deepened.append(row)
            row = []
        row.append(point_height)
    chunktag_heightmap_deepened.append(row)

    return chunktag_heightmap_deepened

# generate 2d heightmap matrix
def create_chunktile(world, chunk_x, chunk_z):

    chunk_tile = ChunkTile()
    chunk_tile.anvil_file = chunk.load(world, chunk_x, chunk_z)
    chunk_tile.chunktag_heightmap = get_chunktag_heightmap(chunk_tile.anvil_file.data, tags[1])

    surface_blocks = yaml_open.get("surface_blocks")

    # generate heightmap
    heightmap = []

    for z in range(16):
        row = []

        for x in range(16):
            start = chunk_tile.chunktag_heightmap[z][x] - 1
            for y in range(start, 0, -1):
                block = chunk_tile.anvil_file.get_block(x, y, z).id

                if block in surface_blocks:
                    row.append(y)
                    break

        heightmap.append(row)

    chunk_tile.heightmap = heightmap
    return chunk_tile


def create_heightmap(world, chunk_x1, chunk_z1, chunk_x2, chunk_z2):

    chunks_to_retrieve = (chunk_x2+1 - chunk_x1) * (chunk_z2+1 - chunk_z1)

    heightmap = []
    chunks_retrieved = 0

    # + 1 because ending chunks are inclusive
    for z in range(chunk_z1, chunk_z2 + 1):
        chunk_row = []

        for x in range(chunk_x1, chunk_x2 + 1):
            chunk_row.append(create_chunktile(world, x, z))

            chunks_retrieved += 1
            progressbar._print(
                chunks_retrieved,
                chunks_to_retrieve,
                1,
                "chunks retrieved"
            )

        heightmap.append(chunk_row)

    return Heightmap(heightmap)
