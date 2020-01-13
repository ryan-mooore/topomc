import os, sys

try:
    import yaml
except:
    raise Exception("Yaml is not installed or is missing")

def yaml_open(object):
    try:
        with open("common/settings.yml", "r") as settings:
            settings = yaml.full_load(settings)
            return settings[object]
    except:
        raise Exception("settings.yaml is incorrectly formatted or missing")
