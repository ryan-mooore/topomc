enum = enumerate

def vectorize(heightmap):
    chunk =  heightmap.chunks[0][0]
    bitmap = [[0 for  element in chunk.cells] for element in chunk.cells[0]]
    print(chunk.get_extremes())

    #for height in range(*chunk.get_extremes()):
    for height in range(chunk.get_extremes()[0], chunk.get_extremes()[0] + 1):
        for y, row in enum(chunk.cells):
            for x, cell in enum(row):
                if bitmap[y][x] is not 1:
                    for isoline in cell.isolines:
                        if isoline.height == height:
                            bitmap = isoline_explore(chunk, cell, cell, isoline.coords[0], height, 0, bitmap)
                            print("--------")



    import pprint
    pp = pprint.PrettyPrinter()
    pp.pprint(bitmap)

def isoline_explore(chunk, cell, startcell, linkcoords, height, iteration, bitmap):
    print(f"x: {cell.x}      y: {cell.y}      linkcoords: {linkcoords}")
    for isoline in cell.isolines:
        if isoline.height == height: #check for operating height
            if (cell.x, cell.y) == (startcell.x, startcell.y) \
                and iteration is not 0: # if trail has looped back to start tile
                bitmap[cell.y][cell.x] = 1
                return bitmap

                # if trail has reached rendering border
            if cell.x == 0 and isoline.coords[0][0] == 0: 
                bitmap[cell.y][cell.x] = 1
                return bitmap
            if cell.x == 14 and isoline.coords[1][0] == 1: 
                bitmap[cell.y][cell.x] = 1
                return bitmap
            if cell.y == 0 and isoline.coords[0][1] == 1: 
                bitmap[cell.y][cell.x] = 1
                return bitmap
            if cell.y == 14 and isoline.coords[1][1] == 0:
                bitmap[cell.y][cell.x] = 1
                return bitmap
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
                    bitmap = bitmap
                        )
