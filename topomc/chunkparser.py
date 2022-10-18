import logging
import math
import os
import sys
import platform

from anvil import Region, Chunk  # type: ignore
from common.logger import Logger
from nbt.nbt import TAG_Int  # type: ignore

VERSION_TAG_INDEX = 1

DEFAULT_SAVES = {
    "windows": "%appdata%\\.minecraft\\saves",
    "darwin": "~/Library/Application Support/minecraft/saves",
    "linux": "~/.minecraft/saves/",
}


class ChunkParser:
    def __init__(self, world: str, saves_path: str = None) -> None:
        self.world = world

        if not saves_path:
            saves_path = DEFAULT_SAVES[platform.system().lower()]

        saves_path = os.path.normcase(saves_path)
        if saves_path.startswith("~"):
            saves_path = os.path.expanduser(saves_path)
        saves_path = os.path.expandvars(saves_path)
        if not os.path.isdir(saves_path):
            Logger.log(logging.critical, f"App: Could not read path: {saves_path}")
            raise NotADirectoryError

        self.world_path = os.path.join(saves_path, self.world)

        # test to see whether world exists
        if not os.path.isdir(self.world_path):
            Logger.log(logging.critical, "Chunk: Specified world save does not exist!")
            Logger.log(logging.info, "Chunk: Available worlds:")
            for world in os.listdir(saves_path):
                if not world[2:-2].endswith("UNDO"):
                    Logger.log(logging.info, f"Chunk: {world}")
            sys.exit()

    def chunkpos_to_regionpos(self, chunk: int) -> int:
        return int(math.floor(chunk / 32))

    def load_at(self, chunkx: int, chunkz: int) -> tuple[Region, TAG_Int]:

        (regionx, regionz) = tuple(
            [
                self.chunkpos_to_regionpos(chunk_coord)
                for chunk_coord in (chunkx, chunkz)
            ]
        )

        anvil_file = os.path.join(
            self.world_path, "region", f"r.{regionx}.{regionz}.mca"
        )

        # open chunk
        try:
            region = Region.from_file(anvil_file)
        except Exception:
            Logger.log(
                logging.critical,
                f"Chunk: Region {regionx, regionz} for chunk {chunkx, chunkz} is not loaded and does not have an save file",
            )
            sys.exit()

        try:
            chunk = Chunk.from_region(region, chunkx, chunkz)
            version_tag = region.chunk_data(chunkx, chunkz)[VERSION_TAG_INDEX]
        except Exception:
            Logger.log(
                logging.critical,
                f"Chunk: Chunk {chunkx, chunkz} is not loaded or corrupt",
            )
            sys.exit()

        return chunk, version_tag
