#dependencies
try:
    import pyglet
except:
    raise Exception("Pyglet is not installed or is missing")



#draw map using pyglet
def draw(data, scale):

    max_len = max(len(data) + 1, len(data[0]) + 1)

    scale = int(16 / max_len * 30 * scale)


    #create canvas
    window = pyglet.window.Window(
        scale * 2 * len(data[0]),
        scale * 2 * len(data)
    )

    #set bg to white
    pyglet.gl.glClearColor(1, 1, 1, 1)

    def draw_line(points):
        scaled_points = [int(point * scale) for point in points]
        pyglet.graphics.draw(
            2, pyglet.gl.GL_LINES,
            ('v2i', (scaled_points)),
            ('c3B', (209, 92, 0, 209, 92, 0))
        )



    #for debugging only

    def draw_grid():
        for i in range(len(data[0])):
            draw_line([arg * 2 for arg in [i, 0, i, scale * len(data)]])

        for i in range(len(data)):
            draw_line([arg * 2 for arg in [0, i, scale * len(data[0]), i]])





    #window event loop here
    @window.event
    def on_draw():
        window.clear()
        #TODO: clean this shit up lol
        for y, row in enumerate(data):
            for x, line_data in enumerate(row):
                #account for empty square
                if line_data:
                    for line_set in line_data:
                        #account for saddle points
                        for index, point in enumerate(line_set[::2]):
                            #translate string to tuple with co-ords
                            (start, end) = point, line_set[index + 1]
                            #position in list + tuple inside square + 1
                            draw_line((
                                x * 2 + start[0] * 2,
                                len(data) * 2 - y * 2 - 2 + start[1] * 2,
                                x * 2 + end[0] * 2,
                                len(data) * 2 - y * 2 - 2 + end[1] * 2
                            ))

    pyglet.app.run()
