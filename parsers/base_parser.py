import datetime

import pytz


class BaseParser(object):
    def __init__(self, config):
        self.config = config
        self.settings = self._get_settings()

        self.timezone = pytz.timezone(config.timezone)
        self.now = datetime.datetime.now(self.timezone)

    def _get_settings(self):
        parser = self.__module__.split('.')[-1]
        return self.config.parsers[parser]

    def run(self):
        raise NotImplementedError
