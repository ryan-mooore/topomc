from functools import cache
from os import mkdir, path

import numpy as np
from anvil import Chunk, Region
from anvil.errors import ChunkNotFound
from tifffile import imwrite

# This was the last version where heightmap data was streammed across bits. See:
# https://minecraft.fandom.com/wiki/Chunk_format (under Heightmaps)
V1_15_2 = 2230

# This was the first snapshot that included the increased 1.17 height limit. See: 
# https://minecraft.fandom.com/wiki/Java_Edition_21w06a
V21W06A = 2694

# Buffer which will be cropped in the R script to remove smoothed geometry
CROP_BUFFER = 16

# Extend Chunk class from anvil-parser to include native heightmap support
class ChunkWithHeightmap(Chunk):
    def __init__(self, *args):
        self.heightmap = np.mat(np.empty((16, 16)))
        super().__init__(*args)

@cache
def region_at(world, rx, rz):
    try:
        filename = f"r.{rx}.{rz}.mca"
        print(f"generate: Reading {filename}...")
        return Region.from_file(path.join(world, "region", filename))
    except FileNotFoundError:
        print(f"Warning: region ({rx}) ({rz}) not loaded")
        return None

@cache
def chunk_at(region, cx, cz):
    try:
        chunk = ChunkWithHeightmap.from_region(region, cx, cz)
    except KeyError:
        raise Exception("Error parsing NBT data. Is the world derived from a 1.18 version?")
    except ChunkNotFound:
        print(f"Warning: chunk ({cx}) ({cz}) not loaded")
        return None
    if not chunk.data["Heightmaps"]:
        print(f"Warning: heightmaps not loaded for chunk ({cx}) ({cz})")
        return None
    if not chunk.data["Heightmaps"].get("MOTION_BLOCKING"):
        print(f"Warning: MOTION_BLOCKING heightmap not loaded for chunk ({cx}) ({cz})")
        return None

    block = 0
    block_value = 0
    bit_of_value = 0

    # Decode heightmap data stream
    for data_long in chunk.data["Heightmaps"]["MOTION_BLOCKING"]:
        for bit_of_long in range(64): # 64 bits per long
            curr_bit = (data_long >> bit_of_long) & 0x01
            block_value = (curr_bit << bit_of_value) | block_value
            bit_of_value += 1
            # 9 bits per heightmap value (See: https://minecraft.fandom.com/wiki/Chunk_format)
            if bit_of_value >= 9:
                chunk.heightmap[block // 16, block % 16] = block_value
                block += 1
                if block == 256:
                    return chunk
                block_value = 0
                bit_of_value = 0
        if chunk.version > V1_15_2:
            bit_of_value = 0

def to_tiffs(settings):
    world_path = path.expanduser(path.join(
        settings["saves_path"],
        settings["world"],
    ))

    bx1 = settings["bounding_points"][0] - CROP_BUFFER 
    bz1 = settings["bounding_points"][1] - CROP_BUFFER
    bx2 = settings["bounding_points"][2] + CROP_BUFFER
    bz2 = settings["bounding_points"][3] + CROP_BUFFER

    create_mat = lambda dtype : np.mat(np.zeros((
        (bz2 - bz1) // settings["downsample"] + 1, 
        (bx2 - bx1) // settings["downsample"] + 1
    )), dtype=dtype)
    np.any
    data = {
        "dem": create_mat(np.uint8) if settings["compress_height_limit"] else create_mat(np.uint16),
        "vegetation": create_mat(np.bool_),
        "landcover": create_mat(np.uint8)
    }

    print("generate: Reading data...")
    for row, bz in enumerate(range(bz1, bz2, settings["downsample"])):
        for col, bx in enumerate(range(bx1, bx2, settings["downsample"])):
            cz, cx = bz // 16, bx // 16
            rz, rx = cz // 32, cx // 32
            bz_in_c = bz % 16
            bx_in_c = bx % 16
            entry = row, col

            region = region_at(world_path, rx, rz)
            if not region: continue
            chunk = chunk_at(region, cx, cz)
            if not chunk: continue

            if chunk.version >= V21W06A:
                if settings["compress_height_limit"]:
                    max_height = min(int(chunk.heightmap[bz_in_c, bx_in_c]) - 64, 255)
                    min_height = 0
                else:
                    max_height = int(chunk.heightmap[bz_in_c, bx_in_c]) - 64
                    min_height = -64

            else:
                max_height = int(chunk.heightmap[bz_in_c, bx_in_c]) if chunk.heightmap.any() else 255
                min_height = 0

            for by in range(max_height, min_height, -1):
                block = chunk.get_block(bx_in_c, by, bz_in_c)
                
                # -- surface processes: dem and landcover --
                if block.id in settings["surface_blocks"]:
                    data["dem"][entry] = by
                    data["landcover"][entry] = settings["surface_blocks"].index(block.id)
                    break
                elif "water" in settings["surface_blocks"]:
                    # inherently waterlogged blocks, see https://minecraft.fandom.com/wiki/Waterlogging
                    if block.id in ["seagrass", "tall_seagrass", "kelp", "kelp_plant"]:
                        data["dem"][entry] = by
                        data["landcover"][entry] = settings["surface_blocks"].index("water")
                        break
                    # waterlogged blocks
                    elif block.properties.get("waterlogged"):
                        if block.properties["waterlogged"] == "true" and "water" in settings["surface_blocks"]:
                            data["dem"][entry] = by
                            data["landcover"][entry] = settings["surface_blocks"].index("water")
                            break
                
                # -- other processes: vegetation --
                if block.id.endswith("leaves"):
                    data["vegetation"][entry] = 1

    print("generate: Writing data...")
    try:
        mkdir("data")
    except FileExistsError:
        pass
    bits = {
        0: 1,
        2: 8,
        4: 16
    }
    for layer, data in data.items():
        filename = f"data/{layer}.tif"
        print(f"generate: Writing {filename}...")
        imwrite(
            filename,
            np.kron(data, np.ones(np.repeat(settings["downsample"], 2), dtype=data.dtype)),
            bitspersample=bits[data.dtype.num]
        )