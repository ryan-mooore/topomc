import logging
import sys
import yaml

def get(key):
    try:
        with open("settings.yml", "r") as stream:
            settings = yaml.full_load(stream)
            for setting in settings:
                if setting.lower() == key:
                    return settings[setting]

        logging.fatal(f"Yaml: The setting {key} was not found")
        sys.exit()
    except Exception as e:
        logging.fatal("Yaml: settings.yml is incorrectly formatted or missing")
        raise e

