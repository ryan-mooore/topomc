from os import mkdir, path

import numpy as np
from anvil import Chunk, Region
from tifffile import imwrite

from topomc import decode


def region_at(world_path, rx, rz):
    return Region.from_file(path.join(
        world_path,
        "region", 
        f"r.{rx}.{rz}.mca"
    ))


def chunk_at(region, cx, cz):
    return Chunk.from_region(region, cx, cz)


def get_chunk_hm(region, chunk, cx, cz):
    INDEX_OF_HEIGHTMAPS = 6
    VERSION_TAG_INDEX = 1
    STREAM_BITS_PER_VALUE = 9
    STREAM_INT_SIZE = 64

    version_tag = region.chunk_data(cx, cz)[VERSION_TAG_INDEX]
    data_stream = chunk.data.tags[INDEX_OF_HEIGHTMAPS].tags[2]

    return decode.unstream(
        data_stream, version_tag, STREAM_BITS_PER_VALUE, STREAM_INT_SIZE
    )


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
        chunk = chunk_at(region, cx, cz)
        hm = get_chunk_hm(region, chunk, cx, cz)
        return foreach_within_bound(iter_block, (chunk, hm), cx, cz, 16, bx1, bx2, bz1, bz2)


    def iter_block(chunk, bx, bz):
        chunk, hm = chunk
        bx_relative = bx % 16
        bz_relative = bz % 16

        dem = 0
        vegetation = 0
        landcover = 0


        for by in range(int(hm[bz_relative, bx_relative]) - 1, 0, -1):
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
    