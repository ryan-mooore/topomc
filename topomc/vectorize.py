enum = enumerate

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other): 
        return self.x == other.x and self.y == other.y

def vectorize(heightmap):
    chunk =  heightmap.chunk_tiles[0][0]
    bitmap = [[0 for  element in chunk.cells] for element in chunk.cells[0]]
    print(chunk.get_extremes())

    #for height in range(*chunk.get_extremes()):
    for height in range(chunk.get_extremes()[0], chunk.get_extremes()[0] + 1):
        for y, row in enum(chunk.cells):
            for x, cell in enum(row): #foreach cell
                if bitmap[y][x] is not 1: #if it has not already been used at this height
                    for isoline in cell.isolines:
                        if isoline.height == height: #explore

                            startcell = cell
                            currcell = cell
                            linkcoords = isoline.coords.start
                            line = []

                            for mode in ("search", "trace"):
                                trace = True
                                iteration = 0

                                while trace:
                                    isoline = currcell.isolines[0]
                                    if not currcell.isolines:
                                        trace = False
                                        continue
                                    if isoline.height == height: #check for operating height
                                        
                                        def swap_endpoints():
                                            if linkcoords == isoline.coords.start:
                                                return isoline.coords.end
                                            if linkcoords == isoline.coords.end:
                                                return isoline.coords.start

                                        if iteration != 0:
                                            if (currcell.coords.x, currcell.coords.y) == (startcell.coords.x, startcell.coords.y):
                                                bitmap[currcell.coords.y][currcell.coords.x] = 1
                                                trace = False
                                                continue

                                                # if trail has reached rendering border
                                            if mode == "trace":
                                                line.append((currcell.coords.x, currcell.coords.y))
                                            
                                            if currcell.coords.x == 0 and isoline.coords.start.x == 0: 
                                                bitmap[currcell.coords.y][currcell.coords.x] = 1
                                                linkcoords = swap_endpoints()
                                                trace = False
                                                continue
                                            if currcell.coords.x == 14 and isoline.coords.end.x == 1: 
                                                bitmap[currcell.coords.y][currcell.coords.x] = 1
                                                linkcoords = swap_endpoints()
                                                trace = False
                                                continue
                                            if currcell.coords.y == 0 and isoline.coords.start.y == 1: 
                                                bitmap[currcell.coords.y][currcell.coords.x] = 1
                                                linkcoords = swap_endpoints()
                                                trace = False
                                                continue
                                            if currcell.coords.y == 14 and isoline.coords.end.y == 0:
                                                bitmap[currcell.coords.y][currcell.coords.x] = 1
                                                linkcoords = swap_endpoints()
                                                trace = False
                                                continue
                                            
                                        link_endpoint = swap_endpoints()

                                        if link_endpoint.x in [0, 1]: #if touches x edge
                                            if link_endpoint.x == 0:
                                                new_cell = chunk.cells[currcell.coords.y][currcell.coords.x - 1] #touching left
                                                new_cell_link_endpoint = Coordinates(1, link_endpoint.y)
                                            if link_endpoint.x == 1: #touching right
                                                new_cell = chunk.cells[currcell.coords.y][currcell.coords.x + 1]
                                                new_cell_link_endpoint = Coordinates(0, link_endpoint.y)
                                        if link_endpoint.y in [0, 1]: #if touches y edge
                                            if link_endpoint.y == 0: #touching bottom
                                                new_cell = chunk.cells[currcell.coords.y + 1][currcell.coords.x]
                                                new_cell_link_endpoint = Coordinates(link_endpoint.x, 1)
                                            if link_endpoint.y == 1: #touching top
                                                new_cell = chunk.cells[currcell.coords.y - 1][currcell.coords.x]
                                                new_cell_link_endpoint = Coordinates(link_endpoint.x, 0)
                                        
                                        bitmap[currcell.coords.y][currcell.coords.x] = 1

                                        linkcoords = new_cell_link_endpoint
                                        iteration =+ 1
                                        currcell = new_cell

    print(line)
    import pprint
    pp = pprint.PrettyPrinter()
    pp.pprint(bitmap)