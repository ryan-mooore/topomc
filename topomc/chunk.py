# core
import math
import os

# dependencies
try:
    from anvil import Region as AnvilRegion
    from anvil import Chunk as AnvilChunk
except ImportError:
    raise Exception("Anvil-parser is not installed or is missing")

# files
from common import yaml_open, bin

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
    def __init__(self, world, chunkx, chunkz):

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

        (regionx, regionz) = tuple([
            self.chunkpos_to_regionpos(chunk_coord) for chunk_coord in (chunkx, chunkz)
        ])

        anvil_file = world_path + "/region/r.{}.{}.mca".format(regionx, regionz)

        # open chunk
        try:
            region = AnvilRegion.from_file(anvil_file)
        except Exception:
            raise Exception("Unloaded chunk(s)!")

        self.data = AnvilChunk.from_region(region, chunkx, chunkz)
        
    def generate_heightmap(self):

        surface_blocks = yaml_open.get("surface_blocks")

        self.get_builtin(tags[1])

        # generate heightmap
        self.heightmap = []

        for z in range(16):
            current_row = []

            for x in range(16):
                start = self.heightmap_builtin[z][x] - 1
                for y in range(start, 0, -1):
                    block = self.data.get_block(x, y, z).id

                    if block in surface_blocks:
                        current_row.append(y)
                        break

            self.heightmap.append(current_row)
        
        hm_flat = [y for x in self.heightmap for y in x]
        
        self.min_height = min(*hm_flat)
        self.max_height = max(*hm_flat)


    def get_builtin(self, tag="MOTION_BLOCKING_NO_LEAVES"):

        try:
            tags.index(tag)
        except Exception:
            raise Exception("Invalid tag")

        INDEX_OF_TAG = tags.index(tag)


        # get heightmap data

        try:
            hm_data_stream = \
                self.data.data.tags[INDEX_OF_HEIGHTMAPS].tags[INDEX_OF_TAG]
        except Exception:
            raise Exception("Unloaded chunk(s)!")

        self.data_builtin = bin.unstream(
            hm_data_stream, STREAM_BITS_PER_VALUE, STREAM_INT_SIZE
        )

        self.heightmap_builtin = []
        current_row = []
        for index, point_height in enumerate(self.data_builtin):
            if index % 16 == 0:
                if current_row:
                    self.heightmap_builtin.append(current_row)
                current_row = []
            current_row.append(point_height)
        self.heightmap_builtin.append(current_row)


    def chunkpos_to_regionpos(self, chunk):
        '''convert chunk coords to region coords'''
        return int(math.floor(chunk / 32))