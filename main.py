import os
import anvil
import pyglet

def read_chunk(world_name, regionx, regionz, chunkx, chunkz):
    path_file = open("path_to_saves.txt", "r")
    saves_path = path_file.readline()
    path_file.close()

    path = saves_path + world_name + "/region/r.{}.{}.mca".format(regionx, regionz)

    surface_blocks = ["grass_block", "dirt", "coarse_dirt", "sand", "clay", "podzol"]

    region = anvil.Region.from_file(path)
    chunk = anvil.Chunk.from_region(region, chunkx, chunkz)

    height_map = []

    for z in range (16):
        current_row = []
        for x in range (16):
            for y in range(255, 0, -1):
                block = chunk.get_block(x, y, z).id
                if block in surface_blocks:
                    current_row.append(y)
                    break
        height_map.append(current_row)

    return height_map



def marching_squares(heightmap):
    res = []
    for y in range(len(heightmap) - 1):
        res_row = []
        for x in range(len(heightmap[0])- 1):
            res_element = []
            case = [
                heightmap[y][x],
                heightmap[y][x + 1], 
                heightmap[y + 1][x + 1],
                heightmap[y + 1][x]
            ]
            bitmap = map(lambda e: e >= heightmap[y][x], case)
            bitmap = list(bitmap)

            if bitmap[0] != bitmap[1]: res_element.append("top")
            if bitmap[1] != bitmap[2]: res_element.append("right")
            if bitmap[2] != bitmap[3]: res_element.append("bottom")
            if bitmap[3] != bitmap[0]: res_element.append("left")
            
            res_row.append(res_element)
        res.append(res_row)

    return res



def draw(data, scale):
    translate = {
        "left": (-1, 0),
        "top": (0, 1),
        "right": (1, 0),
        "bottom": (0, -1),
    }

    window = pyglet.window.Window(scale * 15, scale * 15)

    def draw_line(x1, y1, x2, y2):
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES, ('v2i', (x1 * 25, y1 * 25, x2 * 25, y2 * 25)))

    def draw_grid():
        for i in range(15):
            draw_line(2 * i, 0, 2 * i, 15 * scale) 
            draw_line(0, 2 * i, 15 * scale, 2 * i)


    @window.event
    def on_draw():
        window.clear()

        y = 0
        for row in data:
            x = 0
            for element in row:
                if element:
                    start = translate[element[0]]
                    end = translate[element[1]]
                
                
                    draw_line(
                        1 + x * 2 + start[0],
                        15 * 2 - y * 2 + start[1] - 1,
                        1 + x * 2 + end[0],
                        15 * 2 - y * 2 + end[1] - 1
                    )
                x += 1
            y += 1

    pyglet.app.run()


heightmap = read_chunk("test", 0, 0, 1, 3)
data = marching_squares(heightmap)
draw(data, 50)