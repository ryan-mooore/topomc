import sys
#import argparse
# files
from common import yaml_open
import heightmap as hm
import marching_squares
import draw
import vectorize
import logging

try:
    from matplotlib import pyplot
    from scipy.ndimage import gaussian_filter1d
    import anvil
except ImportError as e:
    logging.critical("Main: Dependencies not installed")
    raise e

version = sys.version_info
if version.major == 2:
    logging.critical("Main: Unsupported Python version")
    sys.exit()
if version.major == 3 and version.minor < 7:
    logging.critical("Main: Unsupported Python version")
    sys.exit()


#parser = argparse.ArgumentParser(description='Generate a map')
#parser.add_argument('Bounding co-ordinates', metavar='C', type=int, nargs=4, help='Bounding co-ordinates')
#parser.add_argument('World', metavar='W', nargs=1, help='World')
#parser.add_argument('--World', metavar='W', nargs=1, help='World')
logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s', level=10)

def run(args):
    try:
        bounding_points = (x1, z1, x2, z2) = [int(x) for x in args[1:5]]
    except ValueError:
        logging.critical("App: no co-ordinates for world specified")
        return 1
    if x1 > x2 or z1 > z2:
        logging.critical("App: Invalid co-ordinates")
        return 1

    total_bound_chunks = (x2+1 - x1) * (z2+1 - z1)

    try:
        world = args[5]
    except IndexError:
        logging.info("App: No world found, using default")
        world = yaml_open.get("world")

    try:
        contour_interval = int(args[6])
    except IndexError:
        logging.info("App: None or invalid contour interval found, using default")
        contour_interval = yaml_open.get("interval")

    contour_offset = yaml_open.get("phase")

    heightmap = hm.Heightmap(world, *bounding_points)

    if not isinstance(contour_interval, int) \
    or not isinstance(contour_offset, int):
        logging.critical("App: Contour interval/offset must be an integer")

    marching_squares.square_march(heightmap, contour_interval)
    if not "--debug" in args:
        topodata = vectorize.Topodata(heightmap)
        smoothness = yaml_open.get("smoothness")
        index = yaml_open.get("index")
        save_loc = yaml_open.get("pdf save location")
        line_width = yaml_open.get("line width")
        if save_loc:
            if not save_loc.endswith(".pdf"):
                if save_loc.endswith("/"):
                    save_loc = save_loc + "map.pdf"
                else:
                    save_loc = save_loc + ".pdf"
        draw.draw(topodata, smoothness, index, save_loc, line_width)
    else:
        draw.debug(heightmap)