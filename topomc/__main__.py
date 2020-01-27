import app
import sys

VersionError = Exception("topomc does not run on this version of python")

if __name__ == "__main__":
    version = sys.version_info
    if version.major == 2:
        raise VersionError
    if version.major == 3 and version.minor < 7:
        raise VersionError

    app.run(sys.argv)
