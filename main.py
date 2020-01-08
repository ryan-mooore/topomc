
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
    try:
        world = sys.argv[1]
    except:
        raise Exception("No world specified")

    try:
        args = [int(x) for x in sys.argv[2:6]]
    except:
        raise Exception("no co-ordinates for world specified")

    if args[0] > args[2] or args[1] > args[3]:
        raise Exception("Invalid co-ordinates")

    heightmap = heightmap.create(world, *args)

    data = marching_squares.marching_squares(heightmap)

    scale = yaml_open.get("window_scale")
    draw.draw(data, scale)

    pass
