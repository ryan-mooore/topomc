from marching_squares import Coordinates
import logging
from common import progressbar

class Topodata:
    def __init__(self, heightmap):
        self.heightplanes = []

        (low, high) = heightmap.get_extremes()
        for height in range(*heightmap.get_extremes()):
            heightplane = Heightplane(height, heightmap.cells, heightmap.start_coords, heightmap.end_coords)
            self.heightplanes.append(heightplane)
            progressbar._print(
                height + 1 - low,
                high - low,
                2,
                f"heightplanes created"
            )

class Isoline:
    def __init__(self):
        self.contour = []
        self.direction = 0
        self.closed = False

class Heightplane:
    def __init__(self, height, all_cells, start, end):
        def pixline_tracer(first_iter=False, isoline=Isoline(), this_cell=None, this_cell_link=None):
        # globals: heightplane (reassigned), height (static), origin_cell (static)

            def swap_endpoints():
                if this_cell_link == this_pixline.coords.start:
                    return this_pixline.coords.end
                elif this_cell_link == this_pixline.coords.end:
                    return this_pixline.coords.start
                else:
                    return None
            
            def cell_link_helper(cell_offset, link_offset):
                global new_cell
                global new_cell_link
                (cell_offset_x, cell_offset_y) = cell_offset
                (link_offset_x, link_offset_y) = link_offset
                new_cell = all_cells[this_cell.coords.y + cell_offset_y]\
                    [this_cell.coords.x + cell_offset_x]
                if link_offset_x == '~':
                    link_offset_x = opposite_link.x
                if link_offset_y == '~':
                    link_offset_y = opposite_link.y
                new_cell_link = Coordinates(link_offset_x, link_offset_y)
            
            def end_trace():
                this_isoline.contour.append((
                        opposite_link,
                        this_cell.coords
                    ))
                return this_isoline, location

            
            if not this_cell:
                this_cell = origin_cell


            for this_pixline in this_cell.pixlines:
                if this_pixline.height == height:

                    if not this_cell_link:
                        this_cell_link = this_pixline.coords.start

                    if first_iter:
                        this_isoline = Isoline()
                    else:
                        this_isoline = isoline

                    this_isoline.contour.append((
                        this_cell_link,
                        this_cell.coords
                    ))

                    self.bitmap[this_cell.coords.y][this_cell.coords.x] = 1
                    
                    opposite_link = swap_endpoints()
                    if opposite_link == None:
                        continue

                    location = (this_cell, opposite_link)
                    
                    if not first_iter:
                        #loop testing
                        if (this_cell == origin_cell):
                            this_isoline.closed = True
                            return end_trace()
                        
                    #edge testing
                    c = this_cell.coords
                    l = opposite_link
                    if c.x == 0  and 0 == l.x: return end_trace()
                    elif c.x == len(all_cells[0]) - 1 and 1 == l.x: return end_trace()
                    elif c.y == 0  and 1 == l.y: return end_trace()
                    elif c.y == len(all_cells) - 1 and 0 == l.y: return end_trace()

                    # build link
                    if opposite_link.x == 0:   cell_link_helper((-1, 0), (1, '~')) # left
                    elif opposite_link.x == 1: cell_link_helper(( 1, 0), (0, '~')) # right
                    elif opposite_link.y == 0: cell_link_helper(( 0, 1), ('~', 1))  # bottom
                    elif opposite_link.y == 1: cell_link_helper(( 0,-1), ('~', 0)) # top
                    else:
                        logging.warning(f"Vectorization: {start.x + this_cell.coords.x, start.y + this_cell.coords.y}: isoline does not span cell")
                        continue

                    return pixline_tracer(
                        isoline=this_isoline,
                        this_cell=new_cell,
                        this_cell_link=new_cell_link
                    )
            
            logging.warning(f"Vectorization: {start.x + this_cell.coords.x, start.y + this_cell.coords.y}: no isolines could be found")
            return None


        self.height = height
        self.isolines = []
        self.bitmap = [[0 for  cell_row in all_cells[0]] for cell in all_cells]
        

        for y, row in enumerate(all_cells):
            for x, cell in enumerate(row): # foreach cell
                if self.bitmap[y][x] is not 1: #if it has not already been used at this height
                    
                    for pixline in cell.pixlines:
                        if pixline.height == height:
                            break
                    else:
                        continue
                    
                    origin_cell = cell

                    trace = pixline_tracer(
                        first_iter=True,
                    )
                    if trace:
                        (new_origin_cell, new_start_coords) = trace[1]
                    else:
                        logging.error(f"Vectorization: Drawing isoline at height {height} with origin cell {origin_cell.coords.x, origin_cell.coords.y} failed on SEARCH")
                        continue

                    origin_cell = new_origin_cell

                    trace = pixline_tracer(
                        first_iter=True,
                        this_cell_link=new_start_coords
                    )
                    if trace:
                        new_isoline = trace[0]
                    else:
                        logging.error(f"Vectorization: Drawing isoline at height {height} with origin cell {origin_cell.coords.x, origin_cell.coords.y} failed on TRACE")
                        continue
                    self.isolines.append(new_isoline) # only get line value