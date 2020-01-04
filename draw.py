#dependencies
try:
    import pyglet
except:
    raise Exception("Pyglet is not installed or is missing")



#draw map using pyglet
def draw(data, scale = 20):

    #dict for translating strings to xy vaules
    translate = {
        "left": (-1, 0),
        "top": (0, 1),
        "right": (1, 0),
        "bottom": (0, -1),
    }

    #create canvas
    window = pyglet.window.Window(
        scale * 2 * len(data[0]),
        scale * 2 * len(data)
    )

    def draw_line(points):
        scaled_points = [point * scale for point in points]
        pyglet.graphics.draw(
            2, pyglet.gl.GL_LINES,
            (
                'v2i', (scaled_points)
            )
        )



    #for debugging only
    """
    def draw_grid():
        for i in range(len(data[0])):
            draw_line(*[arg * 2 for arg in [i, i, 0, scale * len(data)]])

        for i in range(len(data)):
            draw_line(*[arg * 2 for arg in [0, scale * len(data[0]), i, i]])
    """



    #window event loop here
    @window.event
    def on_draw():
        window.clear()

        #TODO: clean this shit up lol
        for y, row in enumerate(data):
            for x, line_data in enumerate(row):
                #account for empty square
                if line_data:
                    #account for saddle points (TODO: cleanup with iteration)
                    for index, point in enumerate(line_data[::2]):

                        #translate string to tuple with co-ords
                        (start, end) = translate[point], translate[line_data[index + 1]]

                        #position in list + tuple inside square + 1
                        draw_line((
                            x * 2  + start[0] + 1,
                            y * -2 + start[1] - 1 + len(data) * 2,
                            x * 2  + end[0]   + 1,
                            y * -2 + end[1]   - 1 + len(data) * 2
                        ))

    pyglet.app.run()
