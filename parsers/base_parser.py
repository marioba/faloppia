import datetime
import os

import pytz
from datetime import timedelta


class BaseParser(object):
    def __init__(self, manager):
        self.manager = manager
        self.config = manager.config
        self.name = self.__module__.split('.')[-1]
        self.settings = self.config.parsers[self.name]
        self.settings['data_dir'] = os.path.join(
            self.config.data_dir, self.name)

        self.timezone = pytz.timezone(self.config.timezone)
        self.now = datetime.datetime.now(self.timezone)
        self.timespan = timedelta(**self.settings['timespan'])
        self.start = self.now - self.timespan

    def _send_alert(self, level, text):
        self.manager.log_alert(level, text)

    def _log_event(self, level, text):
        self.manager.log_event(level, text)

    def run(self):
        raise NotImplementedError

    def _check_data(self):
        raise NotImplementedError

    def _store_data(self):
        raise NotImplementedError
