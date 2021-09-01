import logging
import sys
from topomc.common.logger import Logger
import yaml


def get(key):
    try:
        with open("settings.yml", "r") as stream:
            settings = yaml.full_load(stream)
            for setting in settings:
                if setting.lower() == key:
                    return settings[setting]

        Logger.log(logging.critical, f"The setting {key} was not found in settings.yml")
        raise KeyError
    except Exception as e:
        Logger.log(
            logging.critical, f"settings.yml is incorrectly formatted or missing"
        )
        raise e


def get_all():
    try:
        with open("settings.yml", "r") as stream:
            return yaml.full_load(stream)
    except Exception as e:
        Logger.log(
            logging.critical, f"settings.yml is incorrectly formatted or missing"
        )
        raise e
