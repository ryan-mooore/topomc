from topomc.common.coordinates import Coordinates
from topomc.common import decode, progressbar, yaml_open
from topomc.preprocesses import chunk

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
    def __init__(self, world, chunk_x, chunk_z):
        
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

            chunktag_heightmap = decode.unstream(
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


        self.anvil_file = chunk.load(world, chunk_x, chunk_z)
        self.chunktag_heightmap = get_chunktag_heightmap(
            self.anvil_file.data, tags[1]
        )

        surface_blocks = yaml_open.get("surface blocks")

        # generate heightmap
        self.heightmap = []


        # TODO:
        # implement generator
        # account for waterlogged blocks

        for z in range(16):
            row = []

            for x in range(16):
                start = self.chunktag_heightmap[z][x] - 1
                for y in range(start, 0, -1):
                    block = self.anvil_file.get_block(x, y, z).id

                    if block in surface_blocks:
                        row.append(y)
                        break

            self.heightmap.append(row)

    def get_extremes(self):
        min_height = 0xFF
        max_height = 0x00

        point_heights = [point_height for row in self.heightmap for point_height in row]
        min_height = min(*point_heights)
        max_height = max(*point_heights)
        
        return (min_height, max_height)
                

class Heightmap:

    def __init__(self, world, chunk_x1, chunk_z1, chunk_x2, chunk_z2):
        
        def horizontal_append(map1, map2):
        # append if map contains content
            if map1:
                for index, row in enumerate(map2):
                    map1[index].extend(row)
            # else create content
            else:
                map1 = map2
            return map1

        def vertical_append(map1, map2):
            # append if map contains content
            if map1:
                for row in map2:
                    map1.append(row)
            # create content
            else:
                map1 = map2
            return map1


        self.chunk_tiles = []
        self.heightmap = []

        # + 1 because ending chunks are inclusive
        for z in range(chunk_z1, chunk_z2 + 1):
            chunk_row = []
            chunk_tile_row = []
            for x in range(chunk_x1, chunk_x2 + 1):
                chunk_tile = ChunkTile(world, x, z)
                chunk_row = horizontal_append(chunk_row, chunk_tile.heightmap)
                
                chunk_tile.coords = Coordinates(x - chunk_x1, z - chunk_z1)
                chunk_tile_row.append(chunk_tile)

            self.heightmap = vertical_append(self.heightmap, chunk_row)
            self.chunk_tiles.append(chunk_tile_row)

            self.start_coords = Coordinates(chunk_x1 * 16, chunk_z1 * 16)
            self.end_coords = Coordinates(chunk_x2 * 16, chunk_z2 * 16)
        
        self.width =  len(self.heightmap[0])
        self.height = len(self.heightmap)

    def get_extremes(self):
        min_height = 0xFF
        max_height = 0x00

        if len(self.chunk_tiles) == 1 and len(self.chunk_tiles[0]) == 1:
            return self.chunk_tiles[0][0].get_extremes()
        else:
            min_heights = [chunk_tile.get_extremes()[0] for row in self.chunk_tiles for chunk_tile in row]
            min_height = min(*min_heights)
            max_heights = [chunk_tile.get_extremes()[1] for row in self.chunk_tiles for chunk_tile in row]
            max_height = max(*max_heights)

        return (min_height, max_height)