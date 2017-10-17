import datetime
import importlib
import logging

import pytz

from app.utils.message_sender import MessageSender
from app.utils.utils import setup_logging, StandardAlertLevels


class ParsersManager(object):
    def __init__(self, config):
        self.config = config
        setup_logging(self.config)

        if self.config.fake_sms_mode:
            logging.debug('fake_sms_mode ON')
            self.config.set_fake_api_call(return_status=500)
        self.parsers = self._get_parsers()

    def run(self):
        """

        :raises: FatalError if an SMS could not be send
        """
        parsed = []
        self.log_event('parsing started', 'using: {}'.format(
            list(self.parsers.keys())))
        for name, instance in self.parsers.items():
            try:
                instance.run()
                parsed.append(name)
            except Exception as e:
                self.log_alert(StandardAlertLevels.it, str(e))
        return parsed

    def log_alert(self, level, text, send_sms=True):
        text = self.config.alert_text['level_{}'.format(level)].format(text)
        if send_sms:
            MessageSender(self.config).send_alert(level, text)
            text = 'New SMS sent: {}'.format(text)
            self._log_event(text)
        else:
            self.log_event('alert without SMS', text)

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
            'app.parsers.{}'.format(parser_name))
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
    # For Debugging
    from app.config import Config

    CONFIG = Config()

    manager = ParsersManager(CONFIG)
    manager.run()
