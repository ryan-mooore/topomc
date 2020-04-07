from matplotlib import pyplot as plt
from scipy.ndimage import gaussian_filter1d
import numpy
# files
from common import progressbar

def draw(data, scale, smooth, smoothness, contour_index, save_loc):   

    plt.figure("Preview")

    width = len(data.heightplanes[0].bitmap[0])
    height = len(data.heightplanes[0].bitmap)

    max_len = max(width + 1, height + 1)
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
            
            if smooth:
                x = gaussian_filter1d(x, smoothness)
                y = gaussian_filter1d(y, smoothness)

            line_width = 0.3

            if heightplane.height % contour_index == 0:
                plt.plot(x, y, "#D15C00", linewidth=line_width * 25/14)
            else:
                plt.plot(x, y, "#D15C00", linewidth=line_width)

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
    graph = plt.gcf()
    
    axes.set_aspect(1)
    axes.set_xlim(0, width)
    axes.set_ylim(0, height)
    
    if save_loc:
        graph.set_size_inches(0.629921 * height / 16, 0.629921 * height / 16) 

        graph.savefig(save_loc)

    for line in axes.lines:
        line.set_linewidth(
            line.get_linewidth() * 2**(4 - numpy.log2(max_len / 15)))
    graph.set_size_inches(8 * scale, 8 * scale) 
    graph.canvas.toolbar.pack_forget()
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)

    plt.show()

def debug(data):
    plt.figure("Preview")

    width = len(data.cells[0])
    height = len(data.cells)

    for y, row in enumerate(data.cells):
            for x, cell in enumerate(row):
                if cell.pixlines:
                    for pixline in cell.pixlines:
                        x = [pixline.coords.start.x + cell.coords.x, pixline.coords.end.x + cell.coords.x]
                        y = [cell.coords.y - pixline.coords.start.y + 1, cell.coords.y - pixline.coords.end.y + 1]
                        plt.plot(x, y, "#D15C00", linewidth=2)

    print("Loading matplotlib window...")
    print()


    #plt.axis("off")
    
    axes = plt.gca()
    graph = plt.gcf()
    
    axes.set_xlim(0, width)
    axes.set_ylim(0, height)
    axes.invert_yaxis()
    axes.set_aspect(1)

    graph.set_size_inches(8, 8) 
    plt.xticks(range(0, width))
    plt.yticks(range(0, height))
    graph.canvas.toolbar.pack_forget()
    #plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.grid(color='#000', linestyle='-', linewidth=0.1, which="both")
    plt.show()