from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d

# files
from common import progressbar

def draw(data, scale, smooth, contour_index):   
    max_len = max(len(data.heightplanes[0].bitmap) + 1, len(data.heightplanes[0].bitmap[0]) + 1)
    isolines_to_render = 0
    for index, heightplane in enumerate(data.heightplanes):
        isolines_to_render += len(heightplane.isolines)

    isolines_rendered = 0
    for index, heightplane in enumerate(data.heightplanes):
        for isoline in heightplane.isolines:
            isoline.vertices = []
            for point in isoline.contour:
                (contour_coords, cell_coords) = point
                isoline.vertices.append((cell_coords.x + contour_coords.x,
                len(heightplane.bitmap) - cell_coords.y - 1 + contour_coords.y))

            x = [vertice[0] for vertice in isoline.vertices]
            y = [vertice[1] for vertice in isoline.vertices]
            
            sigma = 1
            if smooth:
                x = gaussian_filter1d(x, sigma)
                y = gaussian_filter1d(y, sigma)

            if heightplane.height % contour_index == 0:
                plt.plot(x, y, "#D15C00", linewidth=2)
            else:
                plt.plot(x, y, "#D15C00", linewidth=1)

            isolines_rendered += 1
            progressbar._print(
                isolines_rendered,
                isolines_to_render,
                3,
                f"isolines rendered"
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