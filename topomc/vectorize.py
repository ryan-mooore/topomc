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
                            trace = True
                            linkcoords = isoline.coords.start
                            
                            print(f"x: {currcell.coords.x}      y: {currcell.coords.y}      linkcoords: {linkcoords.x, linkcoords.y}")
                            
                            while trace:
                                if not currcell.isolines:
                                    trace = False
                                    continue
                                for isoline in currcell.isolines:
                                    iteration = 0
                                    if isoline.height == height: #check for operating height
                                        if (currcell.coords.x, currcell.coords.y) == (startcell.coords.x, startcell.coords.y) \
                                            and iteration is not 0: # if trail has looped back to start tile
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            trace = False
                                            continue

                                            # if trail has reached rendering border
                                        if currcell.coords.x == 0 and isoline.coords.start.x == 0: 
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            trace = False
                                            continue
                                        if currcell.coords.x == 14 and isoline.coords.end.x == 1: 
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            trace = False
                                            continue
                                        if currcell.coords.y == 0 and isoline.coords.start.y == 1: 
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            trace = False
                                            continue
                                        if currcell.coords.y == 14 and isoline.coords.end.y == 0:
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            trace = False
                                            continue
                                        else:
                                            print(f"coords: {isoline.coords}")
                                            if linkcoords == isoline.coords.start:
                                                newcoords = isoline.coords.end
                                            if linkcoords == isoline.coords.end:
                                                newcoords = isoline.coords.start

                                            if newcoords.x in [0, 1]: #if touches x edge
                                                if newcoords.x == 0:
                                                    newcell = chunk.cells[currcell.coords.y][currcell.coords.x - 1] #touching left
                                                    newlinkcoords = Coordinates(1, newcoords.y)
                                                if newcoords.x == 1: #touching right
                                                    newcell = chunk.cells[currcell.coords.y][currcell.coords.x + 1]
                                                    newlinkcoords = Coordinates(0, newcoords.y)
                                            if newcoords.y in [0, 1]: #if touches y edge
                                                if newcoords.y == 0: #touching bottom
                                                    newcell = chunk.cells[currcell.coords.y + 1][currcell.coords.x]
                                                    newlinkcoords = Coordinates(newcoords.x, 1)
                                                if newcoords.y == 1: #touching top
                                                    newcell = chunk.cells[currcell.coords.y - 1][currcell.coords.x]
                                                    newlinkcoords = Coordinates(newcoords.x, 0)
                                            
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1

                                            print(f"newcoords: {newcoords}")
                                            linkcoords = newlinkcoords
                                            iteration =+ 1
                                            currcell = newcell
                            print("--------")

    import pprint
    pp = pprint.PrettyPrinter()
    pp.pprint(bitmap)