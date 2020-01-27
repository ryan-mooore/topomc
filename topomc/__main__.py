import app
import sys

if __name__ == "__main__":
    version = sys.version_info
    if version.major == 2:
        raise Exception("topomc does not run on this version of python")
    if version.major == 3 and version.minor < 7:
        raise Exception("topomc does not run on this version of python")
    
    app.run(sys.argv)