import app
import sys, argparse, logging

logging.basicConfig(format='%(process)d-%(levelname)s-%(message)s', level=10)

version = sys.version_info

if version.major == 2:
    logging.critical("Main: Unsupported Python version")
    sys.exit()
if version.major == 3 and version.minor < 7:
    logging.critical("Main: Unsupported Python version")
    sys.exit()

parser = argparse.ArgumentParser(description="Generate a map")

parser.add_argument("x1", type=int, help="X value of start chunk")
parser.add_argument("z1", type=int, help="Z value of start chunk")
parser.add_argument("x2", type=int, nargs="?", help="X value of end chunk", default=None)
parser.add_argument("z2", type=int, nargs="?", help="Z value of end chunk", default=None)
parser.add_argument("--debug", '-D', action='store_true', help="Brings up a debug view of selected chunks")
parser.add_argument('-w', "--world", metavar="WORLD", type=str, help="Overrides 'World' setting in settings.yml")
parser.add_argument("-I", dest="interval", metavar="CONTOUR_INT", type=int, help="Overrides 'Interval' setting in settings.yml")

args = parser.parse_args()

if args.x2 is None or args.debug: args.x2 = args.x1
if args.z2 is None or args.debug: args.z2 = args.z1

if __name__ == "__main__":
    app.run(args)
