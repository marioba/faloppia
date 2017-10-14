import datetime

import pytz

from utils.message_sender import MessageSender


class BaseParser(object):
    def __init__(self, manager):
        self.manager = manager
        self.config = manager.config
        self.settings = self._get_settings()

        self.timezone = pytz.timezone(self.config.timezone)
        self.now = datetime.datetime.now(self.timezone)

    def _get_settings(self):
        parser = self.__module__.split('.')[-1]
        return self.config.parsers[parser]

    def _send_alert(self, level, text):
        self.manager.log_event(alert_level, text)
        MessageSender(self.config).send_alert(level, text)

    def run(self):
        raise NotImplementedError
