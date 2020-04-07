import os.path

path = "%appdata%\.minecraft\saves"

if path.startswith("~"):
    path = os.path.expanduser(path)

path = os.path.expandvars(path)