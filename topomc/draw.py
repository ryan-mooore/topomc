# dependencies
try:
    import pyglet
except ImportError:
    raise Exception("Pyglet is not installed or is missing")

# files
from common import progressbar


def draw(data, scale, chunks_to_render):
    """decode data and create pyglet canvas"""
    max_len = max(len(data) + 1, len(data[0]) + 1)

    scale = int(16 / max_len * 60 * scale)

    # create canvas
    window = pyglet.window.Window(
        scale * len(data[0]),
        scale * len(data)
    )

    # set bg to white
    pyglet.gl.glClearColor(1, 1, 1, 1)

    def draw_line(points):
        scaled_points = [int(point * scale) for point in points]
        pyglet.graphics.draw(
            2, pyglet.gl.GL_LINES,
            ('v2i', (scaled_points)),
            ('c3B', (209, 92, 0, 209, 92, 0))
        )

    def draw_grid():
        """draws grid seperating render tiles"""
        for i in range(len(data[0])):
            draw_line([i, 0, i, scale * len(data) / 2])

        for i in range(len(data)):
            draw_line([0, i, scale * len(data[0]) / 2, i])

    @window.event
    def on_draw():
        pyglet.gl.glLineWidth(3)
        window.clear()
        chunks_rendered = 0
        for y, row in enumerate(data):
            for x, line_data in enumerate(row):
                # account for empty square
                if line_data:
                    for line_set in line_data:
                        # account for saddle points
                        for index, point in enumerate(line_set[::2]):
                            # translate string to tuple with co-ords
                            (start, end) = point, line_set[index * 2 + 1]
                            # position in list + tuple inside square + 1
                            draw_line((
                                x + start[0],
                                len(data) - y - 1 + start[1],
                                x + end[0],
                                len(data) - y - 1 + end[1]
                            ))
                            if chunks_rendered < chunks_to_render:
                                chunks_rendered += 1
                                progressbar._print(
                                    chunks_rendered,
                                    chunks_to_render,
                                    2,
                                    "chunks rendered"
                                )

                                if chunks_rendered == chunks_to_render:
                                    print("Loading pyglet window...")
                                    print()

    pyglet.app.run()
