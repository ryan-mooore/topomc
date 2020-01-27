import os, sys

try:
    import yaml
except:
    raise Exception("Yaml is not installed or is missing")

def get(object):
    try:
        with open(os.path.realpath("common/settings.yml"), "r") as stream:
            settings = yaml.full_load(stream)
            return settings[object]
    except:
        raise Exception("settings.yaml is incorrectly formatted or missing")

