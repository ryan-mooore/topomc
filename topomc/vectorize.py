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

    def isoline_explore(first_iter=False, line=[], currcell=None, linkcoords=None):
        # globals: bitmap (reassigned), height (static), startcell (static)

        if not currcell:
            currcell = startcell
        if not linkcoords:
            linkcoords = currcell.isolines[0].coords.start

        isoline = currcell.isolines[0]

        if isoline.height == height: #check for operating height
            
            def swap_endpoints():
                if linkcoords == isoline.coords.start:
                    return isoline.coords.end
                if linkcoords == isoline.coords.end:
                    return isoline.coords.start

            line.append((currcell.coords.x, currcell.coords.y))
            bitmap[currcell.coords.y][currcell.coords.x] = 1
            
            link_endpoint = swap_endpoints()
            
            if not first_iter:
                location = (currcell, link_endpoint)

                #loop testing
                if (currcell == startcell):
                    bitmap[currcell.coords.y][currcell.coords.x] = 1
                    return line, location
                
                #edge testing
                c = currcell.coords
                l = isoline.coords
                if c.x == 0 and l.start.x == 0 or \
                    c.x == 14 and l.end.x == 1 or \
                    c.y == 0 and l.start.y == 1 or \
                    c.y == 14 and l.end.y == 0:
                    return line, location
                

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

            return isoline_explore(
                line=line,
                currcell=new_cell,
                linkcoords=new_cell_link_endpoint
            )
    





    #for height in range(*chunk.get_extremes()):
    for height in range(chunk.get_extremes()[0], chunk.get_extremes()[0] + 1):
        for y, row in enum(chunk.cells):
            for x, cell in enum(row): #foreach cell
                if bitmap[y][x] is not 1: #if it has not already been used at this height
                    for isoline in cell.isolines:
                        if isoline.height == height: #explore

                            startcell = cell
                            linkcoords = isoline.coords.start

                            line, (new_startcell, new_start_coords) = isoline_explore(
                                first_iter=True,
                            )
                            
                            startcell = new_startcell
                            line = isoline_explore(
                                first_iter=True,
                                linkcoords=new_start_coords
                            )[0] # only get line value

    print(line)
    import pprint
    pp = pprint.PrettyPrinter()
    pp.pprint(bitmap)