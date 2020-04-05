from marching_squares import Coordinates

class Topodata:
    def __init__(self, squaremarch):
        self.heightplanes = []
        
        for height in range(*squaremarch.chunk_tile.get_extremes()):
            heightplane = Heightplane(height, squaremarch.chunk_tile.data)
            self.heightplanes.append(heightplane)

class Isoline:
    def __init__(self):
        self.contour = []
        self.direction = 0
        self.closed = False

class Heightplane:
    def __init__(self, height, cells):
        def pixline_tracer(first_iter=False, isoline=Isoline(), this_cell=None, this_cell_link=None):
        # globals: heightplane (reassigned), height (static), origin_cell (static)

            def swap_endpoints():
                if this_cell_link == this_pixline.coords.start:
                    return this_pixline.coords.end
                elif this_cell_link == this_pixline.coords.end:
                    return this_pixline.coords.start
                else:
                    return AttributeError
            
            def cell_link_helper(cell_offset, link_offset):
                global new_cell
                global new_cell_link
                (cell_offset_x, cell_offset_y) = cell_offset
                (link_offset_x, link_offset_y) = link_offset
                new_cell = cells[this_cell.coords.y + cell_offset_y]\
                    [this_cell.coords.x + cell_offset_x]
                if link_offset_x == '~':
                    link_offset_x = opposite_link.x
                if link_offset_y == '~':
                    link_offset_y = opposite_link.y
                new_cell_link = Coordinates(link_offset_x, link_offset_y)
            
            if not this_cell:
                this_cell = origin_cell

            for this_pixline in this_cell.pixlines:
                if this_pixline.height == height:

                    if not this_cell_link:
                        this_cell_link = this_pixline.coords.start

                    this_isoline = isoline
                    
                    this_isoline.contour.append(this_pixline)
                    self.bitmap[this_cell.coords.y][this_cell.coords.x] = 1
                    
                    opposite_link = swap_endpoints()
                    location = (this_cell, opposite_link)
                    
                    if not first_iter:
                        #loop testing
                        if (this_cell == origin_cell): 
                            this_isoline.closed = True
                            return this_isoline, location
                        
                    #edge testing
                    c = this_cell.coords
                    l = this_pixline.coords
                    if c.x == 0  and 0 in [l.start.x, l.end.x]: return this_isoline, location
                    if c.x == 14 and 1 in [l.start.x, l.end.x]: return this_isoline, location
                    if c.y == 0  and 1 in [l.start.y, l.end.y]: return this_isoline, location
                    if c.y == 14 and 0 in [l.start.y, l.end.y]: return this_isoline, location

                    # build link
                    if opposite_link.x == 0:   cell_link_helper((-1, 0), (1, '~')) # left
                    elif opposite_link.x == 1: cell_link_helper(( 1, 0), (0, '~')) # right
                    elif opposite_link.y == 0: cell_link_helper(( 0, 1), ('~', 1))  # bottom
                    elif opposite_link.y == 1: cell_link_helper(( 0,-1), ('~', 0)) # top
                    else:
                        raise AttributeError

                    return pixline_tracer(
                        isoline=this_isoline,
                        this_cell=new_cell,
                        this_cell_link=new_cell_link
                    )

        self.height = height
        self.isolines = []
        self.bitmap = [[0 for  cell_row in cells] for cell in cells[0]]
        
        for y, row in enumerate(cells):
            for x, cell in enumerate(row): # foreach cell
                if self.bitmap[y][x] is not 1: #if it has not already been used at this height
                    
                    for pixline in cell.pixlines:
                        if pixline.height == height:
                            break
                    else:
                        continue
                    
                    origin_cell = cell

                    (new_origin_cell, new_start_coords) = pixline_tracer(
                        first_iter=True,
                    )[1]
                    
                    origin_cell = new_origin_cell
                    self.isolines.append(
                        pixline_tracer(
                            first_iter=True,
                            this_cell_link=new_start_coords
                        )[0]
                    ) # only get line value

def vectorize(heightmap):
    chunk_tile =  heightmap.chunk_tiles[0][0]
    print(chunk_tile.get_extremes())
