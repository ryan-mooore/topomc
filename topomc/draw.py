from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d
import numpy as np

# files
from common import progressbar

def draw(data, scale, chunks_to_render, smooth):   

    max_len = max(len(data.heightplanes[0].bitmap) + 1, len(data.heightplanes[0].bitmap[0]) + 1)

    chunks_rendered = 0
    for index, heightplane in enumerate(data.heightplanes):
        for isoline in heightplane.isolines:
            isoline.vertices = []
            for point in isoline.contour:
                (contour_coords, cell_coords) = point
                isoline.vertices.append((cell_coords.x + contour_coords.x,
                len(heightplane.bitmap) - cell_coords.y - 1 + contour_coords.y))

            points = np.array(isoline.vertices)
            x, y = points.transpose()
            
            sigma = 1
            if smooth:
                x = gaussian_filter1d(x, sigma)
                y = gaussian_filter1d(y, sigma)

            plt.plot(x, y, "#D15C00", linewidth=1)

            chunks_rendered += 1
            progressbar._print(
                chunks_rendered,
                chunks_to_render,
                2,
                "chunks rendered"
            )


    print("Loading matplotlib window...")
    print()


    plt.axis("off")
    axes = plt.gca()
    axes.set_aspect(1)
    graph = plt.gcf()
    graph.set_size_inches(8 * scale, 8 * scale) 
    graph.canvas.toolbar.pack_forget()
    axes.set_xlim(0, len(data.heightplanes[0].bitmap[0]))
    axes.set_ylim(0, len(data.heightplanes[0].bitmap))
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    plt.show()