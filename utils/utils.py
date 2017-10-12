import yaml


def parse_yaml(path):
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


class StandardAlertLevels:
    it = -1
    no_alert = 0
    general = 1
