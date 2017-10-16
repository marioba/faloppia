import datetime
import pytz


class BaseParser(object):
    def __init__(self, manager):
        self.manager = manager
        self.config = manager.config
        self.name = self.__module__.split('.')[-1]
        self.settings = self.config.parsers[self.name]

        self.timezone = pytz.timezone(self.config.timezone)
        self.now = datetime.datetime.now(self.timezone)

    def _send_alert(self, level, text):
        self.manager.log_alert(level, text)

    def run(self):
        raise NotImplementedError
