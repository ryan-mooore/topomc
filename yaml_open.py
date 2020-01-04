#dependencies
try:
    import yaml
except:
    raise Exception("Yaml is not installed or is missing")



def get(object):
    try:
        with open("settings.yaml", "r") as settings:
            settings = yaml.full_load(settings)
            return settings[object]
    except:
        raise Exception("settings.yaml is incorrectly formatted or missing")
