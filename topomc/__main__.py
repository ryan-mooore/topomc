import app
import sys

VersionError = Exception("topomc does not run on this version of python")

if __name__ == "__main__":
    app.run(sys.argv)
