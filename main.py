
#TODO
#refactor marching squares code
#add thickness to contour lines
#add contour interval
#object-orient



#core
import sys

#files
import yaml_open
import heightmap
import marching_squares
import draw



if __name__ == "__main__":
    #test that arguments are included
    try:
        world = sys.argv[1]
    except:
        raise Exception("No world specified")

    try:
        args = [int(x) for x in sys.argv[2:6]]
    except:
        raise Exception("no co-ordinates for world specified")

    #test that x1 and y1 are less than x2 and y2
    if args[0] > args[2] or args[1] > args[3]:
        raise Exception("Invalid co-ordinates")

    total_chunks = (args[2] + 1 - args[0]) * (args[3] + 1 - args[1])

    #create heightmap from selection
    heightmap = heightmap.create(world, *args, total_chunks)

    #create contour data from heightmap
    contour_interval = yaml_open.get("contour_interval")
    contour_offset   = yaml_open.get("contour_offset")


    if type(contour_interval + contour_offset) is not int:
        raise Exception("Contour interval/offset must be an integer")

    data = marching_squares.marching_squares(heightmap, contour_interval)

    #draw contour data
    scale = yaml_open.get("window_scale")
    draw.draw(data, scale, total_chunks)

    pass
