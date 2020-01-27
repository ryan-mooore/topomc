try:
    import yaml
except ImportError:
    raise Exception("Yaml is not installed or is missing")


def get(object):
    '''get yaml object from key'''
    try:
        with open("topomc/common/settings.yml", "r") as stream:
            settings = yaml.full_load(stream)
            return settings[object]
    except Exception:
        raise Exception("settings.yaml is incorrectly formatted or missing")
