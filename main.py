#core
import sys

#dependencies
import yaml_open

#files
import heightmap
import draw
import marching_squares

if __name__ == "__main__":
    try:
        world = sys.argv[1]
    except:
        raise Exception("No world specified")

    try:
        args = [int(x) for x in sys.argv[2:6]]
    except:
        raise Exception("no co-ordinates for world specified")

    heightmap = heightmap.create(world, *args)

    data = marching_squares.marching_squares(heightmap)

    scale = yaml_open.get("window_scale")
    draw.draw(data, scale)

    pass
