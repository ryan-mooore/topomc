enum = enumerate

class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other): 
        return self.x == other.x and self.y == other.y

def vectorize(heightmap):
    chunk =  heightmap.chunks[0][0]
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
                            thread = True
                            linkcoords = isoline.coords.start
                            
                            print(f"x: {currcell.coords.x}      y: {currcell.coords.y}      linkcoords: {linkcoords.x, linkcoords.y}")
                            
                            while thread:
                                if not currcell.isolines:
                                    thread = False
                                    continue
                                for isoline in currcell.isolines:
                                    iteration = 0
                                    if isoline.height == height: #check for operating height
                                        if (currcell.coords.x, currcell.coords.y) == (startcell.coords.x, startcell.coords.y) \
                                            and iteration is not 0: # if trail has looped back to start tile
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            thread = False
                                            continue

                                            # if trail has reached rendering border
                                        if currcell.coords.x == 0 and isoline.coords.start.x == 0: 
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            thread = False
                                            continue
                                        if currcell.coords.x == 14 and isoline.coords.end.x == 1: 
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            thread = False
                                            continue
                                        if currcell.coords.y == 0 and isoline.coords.start.y == 1: 
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            thread = False
                                            continue
                                        if currcell.coords.y == 14 and isoline.coords.end.y == 0:
                                            bitmap[currcell.coords.y][currcell.coords.x] = 1
                                            thread = False
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

def isoline_explore(chunk, cell, startcell, linkcoords, height, iteration, bitmap, mode):

    print(f"x: {cell.x}      y: {cell.y}      linkcoords: {linkcoords}")
    for isoline in cell.isolines:
        if isoline.height == height: #check for operating height
            if (cell.x, cell.y) == (startcell.x, startcell.y) \
                and iteration is not 0: # if trail has looped back to start tile
                bitmap[cell.y][cell.x] = 1
                thread = False

                # if trail has reached rendering border
            if cell.x == 0 and isoline.coords[0][0] == 0: 
                bitmap[cell.y][cell.x] = 1
                thread = False
            if cell.x == 14 and isoline.coords[1][0] == 1: 
                bitmap[cell.y][cell.x] = 1
                thread = False
            if cell.y == 0 and isoline.coords[0][1] == 1: 
                bitmap[cell.y][cell.x] = 1
                thread = False
            if cell.y == 14 and isoline.coords[1][1] == 0:
                bitmap[cell.y][cell.x] = 1
                thread = False
            else:
                print(f"coords: {isoline.coords}")
                if linkcoords == isoline.coords[0]:
                    newcoords = isoline.coords[1]
                if linkcoords == isoline.coords[1]:
                    newcoords = isoline.coords[0]

                if newcoords[0] in [0, 1]: #if touches x edge
                    if newcoords[0] == 0:
                        newcell = chunk.cells[cell.y][cell.x - 1] #touching left
                        newlinkcoords = (1, newcoords[1])
                    if newcoords[0] == 1: #touching right
                        newcell = chunk.cells[cell.y][cell.x + 1]
                        newlinkcoords = (0, newcoords[1])
                if newcoords[1] in [0, 1]: #if touches y edge
                    if newcoords[1] == 0: #touching bottom
                        newcell = chunk.cells[cell.y + 1][cell.x]
                        newlinkcoords = (newcoords[0], 1)
                    if newcoords[1] == 1: #touching top
                        newcell = chunk.cells[cell.y - 1][cell.x]
                        newlinkcoords = (newcoords[0], 0)

                print(f"newcoords: {newcoords}")
                bitmap[cell.y][cell.x] = 1
                return isoline_explore(
                    chunk = chunk,
                    cell = newcell,
                    startcell = startcell, 
                    linkcoords = newlinkcoords,
                    height = height,
                    iteration = iteration + 1,
                    bitmap = bitmap,
                    mode = "explore"
                        )
