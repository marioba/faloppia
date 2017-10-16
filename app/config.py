import os

from app.utils.utils import parse_yaml


class Config(object):
    def __init__(self, dir_path=None, config_file=None):
        # add each attribute of config.yml to Config
        # this can be used like this
        # c = Config()
        # c.alert_numbers

        if dir_path is None:
            dir_path = os.path.dirname(os.path.realpath(__file__))
        if config_file is None:
            config_file = 'config.yml'
        file_path = os.path.join(dir_path, config_file)
        config = parse_yaml(file_path)
        config['data_dir'] = os.path.join(dir_path, 'data')
        config['lock_file'] = os.path.join(
            dir_path, 'data', 'static', 'alerts.json')
        config['debug_log_file'] = os.path.join(
            dir_path, 'logs', 'river_warn_debug.log')
        config['events_log_file'] = os.path.join(
            dir_path, 'logs', 'river_warn_events.log')
        self.__dict__.update(config)
        self.__dict__['fake_api'] = False

    def __setattr__(self, name, value):
        # forbid changing configurations
        raise AttributeError("%s is an immutable attribute." % name)

    def set_fake_api_call(self, fake=True, return_status=202):
        self.__dict__['fake_api'] = fake
        self.__dict__['fake_api_return'] = return_status
