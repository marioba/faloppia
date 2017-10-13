import datetime
import importlib
from random import randint

import pytz

from config import Config
from utils.message_sender import MessageSender
from web import CONFIG


CONFIG = Config()

# TODO REMOVE FAKE STUFF
CONFIG.set_fake_api_call()
FAKE_TEXTS = [
    'nothing special happening',
    'some rain coming',
    'heavy rain coming']

alert_level = randint(0, 2)
text = FAKE_TEXTS[alert_level]
# END REMOVE FAKE STUFF


class ParsersManager(object):
    def __init__(self, config):
        self.config = config
        self.parsers = self._get_parsers()

    def run(self):
        for name, instance in self.parsers.items():
            instance.run()

    def _instantiate_parser(self, parser_name):
        parser_module = importlib.import_module(
            'parsers.{}'.format(parser_name))
        class_name = '{}Parser'.format(parser_name.capitalize())
        parser_class = getattr(parser_module, class_name)
        return parser_class(self.config)

    def _get_parsers(self):
        active_parsers = {}
        for k, v in self.config.parsers.items():
            if v['active']:
                active_parsers[k] = self._instantiate_parser(k)
        return active_parsers

    def log_event(self, level, text):
        tz = pytz.timezone(self.config.timezone)
        now = datetime.datetime.now(tz)
        now = now.strftime('%Y-%m-%d %H:%M:%S%z')
        text = '{}, New alert level {}, {}\n'.format(now, level, text)
        with open(CONFIG.events_log_file, 'a') as f:
            f.write(text)




manager = ParsersManager(CONFIG)._get_parsers()
print(manager)

#log_event(alert_level, text)
#response = MessageSender(CONFIG).send_alert(alert_level, text)
