import logging
import math
import os
import sys

import anvil
from topomc import app


class ChunkParser:

    def __init__(self, world):
        self.world = world
        
        saves_path = app.settings["Saves path"]
        saves_path = os.path.normcase(saves_path)
        if saves_path.startswith("~"):
            saves_path = os.path.expanduser(saves_path)
        saves_path = os.path.expandvars(saves_path)
        if not os.path.isdir(saves_path):
            logging.critical(f"App: Could not read path: {saves_path}")
            raise NotADirectoryError
        
        self.world_path = os.path.join(saves_path, self.world)

        # test to see whether world exists
        if not os.path.isdir(self.world_path):
            logging.critical("Chunk: Specified world save does not exist!")
            logging.info("Chunk: Available worlds:")
            for world in os.listdir(saves_path):
                if not world[2:-2].endswith("UNDO"):
                    logging.info(f"Chunk: {world}")
            sys.exit()

    def chunkpos_to_regionpos(self, chunk):
        return int(math.floor(chunk / 32))

    def load_at(self, chunkx, chunkz):

        (regionx, regionz) = tuple([
            self.chunkpos_to_regionpos(chunk_coord) for chunk_coord in (chunkx, chunkz)
        ])

        anvil_file = os.path.join(self.world_path, "region", f"r.{regionx}.{regionz}.mca")

        # open chunk
        try:
            region = anvil.Region.from_file(anvil_file)
        except Exception:
            logging.critical(f"Chunk: Region {regionx, regionz} for chunk {chunkx, chunkz} is not loaded and does not have an save file")
            sys.exit()

        try:
            chunk = anvil.Chunk.from_region(region, chunkx, chunkz)
        except Exception:
            logging.critical(f"Chunk: Chunk {chunkx, chunkz} is not loaded or corrupt")
            sys.exit()

        return chunk
