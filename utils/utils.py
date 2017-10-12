import logging
import yaml


def parse_yaml(path):
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


class StandardAlertLevels:
    it = -1
    no_alert = 0
    general = 1


class FatalError(RuntimeError):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(FatalError, self).__init__(message)
        logging.fatal(message)
