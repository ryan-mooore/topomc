# dependencies
try:
    import pyglet
except ImportError:
    raise Exception("Pyglet is not installed or is missing")

# files
from common import progressbar


def draw(data, scale, chunks_to_render):
    print(data.heightplanes)
    """decode data and create pyglet canvas"""
    max_len = max(len(data.heightplanes[0].bitmap) + 1, len(data.heightplanes[0].bitmap[0]) + 1)

    scale = int(16 / max_len * 60 * scale)

    # create canvas
    window = pyglet.window.Window(
        scale * len(data.heightplanes[0].bitmap),
        scale * len(data.heightplanes[0].bitmap[0])
    )

    # set bg to white
    pyglet.gl.glClearColor(1, 1, 1, 1)

    def draw_line(points):
        for i in range(len(points) - 1):
            pyglet.graphics.draw(
            2, pyglet.gl.GL_LINES,
            ('v2i', (
                *[int(axis * scale) for axis in points[i]],
                *[int(axis * scale) for axis in points[i+1]]
                )
            ),
            ('c3B', (209, 92, 0, 209, 92, 0))
        )

    def draw_grid():
        """draws grid seperating render tiles"""
        for i in range(len(data.heightplanes[0].bitmap[0])):
            draw_line([(i, 0), (i, scale * len(data.heightplanes[0].bitmap) / 2)])

        for i in range(len(data.heightplanes[0].bitmap)):
            draw_line([(0, i), (scale * len(data.heightplanes[0].bitmap) / 2, i)])

    @window.event
    def on_draw():
        pyglet.gl.glLineWidth(3)
        window.clear()
        # draw_grid()
        chunks_rendered = 0
        for index, heightplane in enumerate(data.heightplanes):
            for isoline in heightplane.isolines:
                isoline.vertices = []
                for point in isoline.contour:
                    (contour_coords, cell_coords) = point
                    isoline.vertices.append((cell_coords.x + contour_coords.x,
                    len(heightplane.bitmap) - cell_coords.y - 1 + contour_coords.y))
                # position in list + tuple inside square + 1
                #if index == 0:
                draw_line(isoline.vertices)
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
