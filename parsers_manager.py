import datetime
import importlib

import pytz

from config import Config


CONFIG = Config()

# TODO REMOVE FAKE STUFF
CONFIG.set_fake_api_call()
# END REMOVE FAKE STUFF


class ParsersManager(object):
    def __init__(self, config):
        self.config = config
        self.parsers = self._get_parsers()

    def run(self):
        self.log_event('parsing started', 'using: {}'.format(
            list(self.parsers.keys())))
        for name, instance in self.parsers.items():
            instance.run()

    def log_alert(self, level, text):
        text = 'New alert level {}, {}'.format(level, text)
        self._log_event(text)

    def log_event(self, title, text):
        text = 'New {}, {}'.format(title, text)
        self._log_event(text)

    def _log_event(self, text):
        tz = pytz.timezone(self.config.timezone)
        now = datetime.datetime.now(tz)
        now = now.strftime('%Y-%m-%d %H:%M:%S%z')
        text = '{}, {}\n'.format(now, text)
        with open(self.config.events_log_file, 'a') as f:
            f.write(text)

    def _instantiate_parser(self, parser_name):
        parser_module = importlib.import_module(
            'parsers.{}'.format(parser_name))
        class_name = '{}Parser'.format(parser_name.capitalize())
        parser_class = getattr(parser_module, class_name)
        return parser_class(self)

    def _get_parsers(self):
        active_parsers = {}
        for k, v in self.config.parsers.items():
            if v['active']:
                active_parsers[k] = self._instantiate_parser(k)
        return active_parsers


if __name__ == '__main__':
    manager = ParsersManager(CONFIG)
    manager.run()
