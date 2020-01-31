from common import bin, progressbar, yaml_open
from chunk import Chunk



class Heightmap:
    def __init__(self, world, chunkx1, chunkz1, chunkx2, chunkz2):
        self.map = []
        self.min_height = 255
        self.max_height = 0
        
        self.chunkx1 = chunkx1
        self.chunkz1 = chunkz1
        self.chunkx2 = chunkx2
        self.chunkz2 = chunkz2
        
        self.total_chunks = \
        (self.chunkx2 + 1 - self.chunkx1) * (self.chunkz2 + 1 - self.chunkz1)

        chunks_retrieved = 0
        
        # + 1 because ending chunks are inclusive
        for z in range(chunkz1, chunkz2 + 1):
            chunk_row = []
            for x in range(chunkx1, chunkx2 + 1):
                current_chunk = Chunk(world, x, z)
                current_chunk.generate_heightmap()
                chunk_row.append(current_chunk)

                if current_chunk.min_height < self.min_height:
                    self.min_height = current_chunk.min_height

                if current_chunk.max_height > self.max_height:
                    self.max_height = current_chunk.max_height

                chunks_retrieved += 1
                progressbar._print(
                    chunks_retrieved,
                    self.total_chunks,
                    1,
                    "chunks retrieved"
                )

            self.map.append(chunk_row)