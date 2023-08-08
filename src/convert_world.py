import logging
import platform
import sys
from argparse import ArgumentParser
from functools import cache
from os import mkdir, path
from pathlib import Path

import numpy as np
from anvil import Chunk, Region
from anvil.errors import ChunkNotFound
from PIL import Image

logging.basicConfig(
    format="generate: (%(levelname)s) %(message)s",
    level=logging.INFO
)

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
        logging.info(f"Reading {filename}...")
        return Region.from_file(path.join(world, "region", filename))
    except FileNotFoundError:
        logging.warning(f"Region ({rx}) ({rz}) not loaded!")
        return None

@cache
def chunk_at(region, cx, cz):
    try:
        chunk = ChunkWithHeightmap.from_region(region, cx, cz)
    except KeyError:
        raise Exception("Error parsing NBT data. Is the world derived from a 1.18 version?")
    except ChunkNotFound:
        logging.warning(f"Chunk ({cx}) ({cz}) not loaded!")
        return None
    if not chunk.data["Heightmaps"]:
        logging.warning(f"Heightmaps not loaded for chunk ({cx}) ({cz})!")
        return None
    if not chunk.data["Heightmaps"].get("MOTION_BLOCKING"):
        logging.warning(f"MOTION_BLOCKING heightmap not loaded for chunk ({cx}) ({cz})")
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

parser = ArgumentParser(description="Generate a map")

parser.add_argument("world", type=str, help="World to map")
parser.add_argument("x1", type=int, help="X value of start chunk")
parser.add_argument("z1", type=int, help="Z value of start chunk")
parser.add_argument("x2", type=int, help="X value of end chunk")
parser.add_argument("z2", type=int, help="Z value of end chunk")
parser.add_argument("-d", "--downsample", type=int, default=1,
    help="Set downsampling level (default: 1)",
)
parser.add_argument("--saves-path", type=Path,
    help="Set a non-standard Minecraft saves path"
)
parser.add_argument("--compress-height-limit", action="store_true",
    help="Compress height limit to 8-bit tiff (0-255)"
)
args = parser.parse_args(sys.argv[1:])

surface_blocks = [line.rstrip() for line in open("surface_blocks.txt") if line.rstrip()]
# structure_blocks = [line.rstrip() for line in open("structure_blocks.txt") if line.rstrip()]

bx1, bz1, bx2, bz2 = args.x1, args.z1, args.x2, args.z2
if bx1 > bx2 or bz1 > bz2:
    logging.critical("Invalid co-ordinates! Exiting...")
    sys.exit()

saves_path = {
    "windows": "%appdata%\\.minecraft\\saves",
    "darwin": "~/Library/Application Support/minecraft/saves",
    "linux": "~/.minecraft/saves/",
}[platform.system().lower()]
if args.saves_path:
    saves_path = args.saves_path
world_path = path.expanduser(path.join(
    saves_path,
    args.world,
))
logging.info(f"Reading data from {world_path}...")

bx1 -= CROP_BUFFER 
bz1 -= CROP_BUFFER
bx2 += CROP_BUFFER
bz2 += CROP_BUFFER

create_mat = lambda dtype : np.mat(np.zeros((
    (bz2 - bz1) // args.downsample + 1, 
    (bx2 - bx1) // args.downsample + 1
)), dtype=dtype)

data = {
    "dem": create_mat(np.uint8) if args.compress_height_limit else create_mat(np.uint16),
    "vegetation": create_mat(np.bool_),
    "landcover": create_mat(np.uint8)
}

for row, bz in enumerate(range(bz1, bz2, args.downsample)):
    for col, bx in enumerate(range(bx1, bx2, args.downsample)):
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
            if args.compress_height_limit:
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
            if block.id in surface_blocks:
                data["dem"][entry] = by
                data["landcover"][entry] = surface_blocks.index(block.id)
                break
            elif "water" in surface_blocks:
                # inherently waterlogged blocks, see https://minecraft.fandom.com/wiki/Waterlogging
                if block.id in ["seagrass", "tall_seagrass", "kelp", "kelp_plant"]:
                    data["dem"][entry] = by
                    data["landcover"][entry] = surface_blocks.index("water")
                    break
                # waterlogged blocks
                elif block.properties.get("waterlogged"):
                    if block.properties["waterlogged"] == "true" and "water" in surface_blocks:
                        data["dem"][entry] = by
                        data["landcover"][entry] = surface_blocks.index("water")
                        break
            
            # -- other processes: vegetation --
            if block.id.endswith("leaves"):
                data["vegetation"][entry] = 1

logging.info("Writing data...")
try:
    mkdir("data")
except FileExistsError:
    pass
for layer, data in data.items():
    filename = f"data/{layer}.tif"
    logging.info(f"Writing {filename}...")
    image = Image.fromarray(np.kron(
        data,
        np.ones(np.repeat(args.downsample, 2),
        dtype=data.dtype)
    ))
    # store downsampling amount as image resolution
    image.save(filename, dpi=tuple(np.repeat(args.downsample * 300, 2)))