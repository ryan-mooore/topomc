from os import mkdir, path

import numpy as np
from anvil import Chunk, Region
from tifffile import imwrite

V1_15 = 2230

def region_at(world_path, rx, rz):
    return Region.from_file(path.join(
        world_path,
        "region", 
        f"r.{rx}.{rz}.mca"
    ))

def get_chunk_hm(chunk):
    result = np.empty(0x100)

    bit_of_long = 0
    curr_height = 0
    block = 0

    for long in chunk.data["Heightmaps"]["MOTION_BLOCKING"]:
        for i in range(0x40):
            bit = (long >> i) & 0x01
            curr_height = (bit << bit_of_long) | curr_height
            bit_of_long += 1
            if bit_of_long >= 9:
                result[block] = curr_height
                block += 1
                if block == 0x100:
                    return result.reshape((16, 16))
                curr_height = 0
                bit_of_long = 0
        if chunk.version > V1_15:
            bit_of_long = 0

def to_tiffs(settings):
    
    def foreach_within_bound(function, outer, outer_x, outer_z, outer_size, inner_min_x, inner_max_x, inner_min_z, inner_max_z):
        min_z = max(outer_z * outer_size, inner_min_z)
        max_z = min(outer_z * outer_size + outer_size - 1, inner_max_z)
        min_x = max(outer_x * outer_size, inner_min_x)
        max_x = min(outer_x * outer_size + outer_size - 1, inner_max_x)
        
        dem_m = []
        veg_m  = []
        land_m  = []
        for z in range(min_z, max_z + 1):
            dem_row = []
            veg_row = []
            land_row = []
            for x in range(min_x, max_x + 1):
                dem, veg, land = function(outer, x, z)
                dem_row.append(dem)
                veg_row.append(veg)
                land_row.append(land)
            dem_m.append(dem_row)
            veg_m.append(veg_row)
            land_m.append(land_row)
        return dem_m, veg_m, land_m


    def iter_chunk(region, cx, cz):
        try:
            chunk = Chunk.from_region(region, cx, cz)
        except KeyError:
            raise Exception("Error parsing NBT data. Is the world derived from a 1.18 version?")
        hm = get_chunk_hm(chunk)
        return foreach_within_bound(iter_block, (chunk, hm), cx, cz, 16, bx1, bx2, bz1, bz2)


    def iter_block(chunk, bx, bz):
        chunk, hm = chunk
        bx_relative = bx % 16
        bz_relative = bz % 16

        dem = 0
        vegetation = 0
        landcover = 0

        max_height = 255
        if hm is not None:
            max_height = int(hm[bz_relative, bx_relative] - 1)

        for by in range(max_height, 0, -1):
            block = chunk.get_block(bx_relative, by, bz_relative).id
            if block in settings["surface_blocks"]:
                dem = by
                landcover = settings["surface_blocks"].index(block)
                break
            if block.endswith("leaves"):
                vegetation = 1
            
        return dem, vegetation, landcover


    bx1, bx2 = settings["bounding_points"][0::2]
    bz1, bz2 = settings["bounding_points"][1::2]

    cx1, cx2 = bx1 // 16, bx2 // 16
    cz1, cz2 = bz1 // 16, bz2 // 16

    rx1, rx2 = cx1 // 32, cx2 // 32
    rz1, rz2 = cz1 // 32, cz2 // 32

    world_path = path.expanduser(path.join(
        settings["saves_path"],
        settings["world"],
    ))

    dem_matrix = []
    vegetation_matrix = []
    landcover_matrix = []
    for rz in range(rz1, rz2 + 1):
        dem_row = []
        vegetation_row = []
        landcover_row = []
        for rx in range(rx1, rx2 + 1):
            print(".", end="")
            region = region_at(world_path, rx, rz)
            dem, vegetation, landcover = foreach_within_bound(iter_chunk, region, rx, rz, 32, cx1, cx2, cz1, cz2)
            dem_row.append(np.bmat(dem).tolist())
            vegetation_row.append(np.bmat(vegetation).tolist())
            landcover_row.append(np.bmat(landcover).tolist())
        dem_matrix.append(dem_row)
        vegetation_matrix.append(vegetation_row)
        landcover_matrix.append(landcover_row)

    try:
        mkdir("data")
    except FileExistsError:
        pass
    imwrite("data/dem.tif", np.bmat(dem).astype("uint16"), bitspersample=16)
    imwrite("data/vegetation.tif", np.bmat(vegetation).astype("uint16"), bitspersample=16)
    imwrite("data/landcover.tif", np.bmat(landcover).astype("uint16"), bitspersample=16)
    