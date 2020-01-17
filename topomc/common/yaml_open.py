import os, sys

try:
    import yaml
except:
    raise Exception("Yaml is not installed or is missing")

def get(object):
    print('bruh: ' + yaml.full_load)
    #try:
    with open(os.path.realpath("topomc/common/settings.yml"), "r") as settings:
        print(settings)
        settings = yaml.full_load(settings)
        return settings[object]
    #except:
        #raise Exception("settings.yaml is incorrectly formatted or missing")

