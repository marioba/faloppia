import os
from utils.utils import parse_yaml


class Config(object):
    def __init__(self):
        # add each attribute of config.yml to Config
        # this can be used like this
        # c = Config()
        # c.alert_numbers
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, 'config.yml')
        config = parse_yaml(file_path)
        config['log_file'] = os.path.join(dir_path, 'logs', 'river_warn.log')
        self.__dict__.update(config)

    def __setattr__(self, name, value):
        # forbid changing configurations
        raise AttributeError("%s is an immutable attribute." % name)
