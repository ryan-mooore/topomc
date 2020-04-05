from marching_squares import Coordinates

def vectorize(heightmap):
    chunk_tile =  heightmap.chunk_tiles[0][0]
    print(chunk_tile.get_extremes())

    def isoline_tracer(first_iter=False, line=[], this_cell=None, this_cell_link=None):
        # globals: bitmap (reassigned), height (static), origin_cell (static)

        def swap_endpoints():
            if this_cell_link == this_isoline.coords.start:
                return this_isoline.coords.end
            elif this_cell_link == this_isoline.coords.end:
                return this_isoline.coords.start
            else:
                return AttributeError
        
        def cell_link_buider(cell_offset, link_offset):
            global new_cell
            global new_cell_link
            (cell_offset_x, cell_offset_y) = cell_offset
            (link_offset_x, link_offset_y) = link_offset
            new_cell = chunk_tile.cells[this_cell.coords.y + cell_offset_y]\
                [this_cell.coords.x + cell_offset_x]
            if link_offset_x == '~':
                link_offset_x = opposite_link.x
            if link_offset_y == '~':
                link_offset_y = opposite_link.y
            new_cell_link = Coordinates(link_offset_x, link_offset_y)
        
        if not this_cell:
            this_cell = origin_cell

        for this_isoline in this_cell.isolines:
            if this_isoline.height == height:

                if not this_cell_link:
                    this_cell_link = this_isoline.coords.start

                line.append((this_cell.coords.x, this_cell.coords.y))
                bitmap[this_cell.coords.y][this_cell.coords.x] = 1
                
                opposite_link = swap_endpoints()
                
                if not first_iter:
                    location = (this_cell, opposite_link)

                    #loop testing
                    if (this_cell == origin_cell): return line, location
                    
                    #edge testing
                    c = this_cell.coords
                    l = this_isoline.coords
                    if c.x == 0  and l.start.x == 0: return line, location
                    if c.x == 14 and l.end.x   == 1: return line, location
                    if c.y == 0  and l.start.y == 1: return line, location
                    if c.y == 14 and l.end.y   == 0: return line, location
                
                # build link
                if opposite_link.x == 0: cell_link_buider((-1, 0), (1, '~')) # left
                if opposite_link.x == 1: cell_link_buider(( 1, 0), (0, '~')) # right
                if opposite_link.y == 0: cell_link_buider(( 0, 1), ('~', 1))  # bottom
                if opposite_link.y == 1: cell_link_buider(( 0,-1), ('~', 0)) # top

                return isoline_tracer(
                    line=line,
                    this_cell=new_cell,
                    this_cell_link=new_cell_link
                )
    





    #for height in range(*chunk_tile.get_extremes()):
    for height in range(chunk_tile.get_extremes()[0], chunk_tile.get_extremes()[0] + 3):
        bitmap = [[0 for  cell_row in chunk_tile.cells] for cell in chunk_tile.cells[0]]
        
        for y, row in enumerate(chunk_tile.cells):
            for x, cell in enumerate(row): #foreach cell
                if bitmap[y][x] is not 1: #if it has not already been used at this height
                    
                    for isoline in cell.isolines:
                        if isoline.height == height:
                            break
                    else:
                        continue
                    
                    origin_cell = cell

                    line, (new_origin_cell, new_start_coords) = isoline_tracer(
                        first_iter=True,
                    )
                    
                    origin_cell = new_origin_cell
                    line = isoline_tracer(
                        first_iter=True,
                        this_cell_link=new_start_coords
                    )[0] # only get line value

                    print(line)
                    import pprint
                    pp = pprint.PrettyPrinter()
                    pp.pprint(bitmap)
