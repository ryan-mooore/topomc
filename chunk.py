import os
import sys
import anvil

path_file = open("path_to_saves.txt", "r")
saves_path = path_file.readline()
path_file.close()

world_name = "test"

path = saves_path + world_name + "/region/r.0.0.mca"

surface_blocks = ["grass_block", "dirt", "coarse_dirt", "sand", "clay", "podzol"]

region = anvil.Region.from_file(path)
chunk = anvil.Chunk.from_region(region, 0, 0)

height_map = []

for z in range (16):
    current_row = []
    for x in range (16):
        for y in range(255, 0, -1):
            block = chunk.get_block(x, y, z).id
            if block in surface_blocks:
                current_row.append(y)
                break
    height_map.append(current_row)

print(height_map)
