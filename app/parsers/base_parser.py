import datetime
import json
import logging
import os
from datetime import timedelta
import dateutil.parser
from json.decoder import JSONDecodeError

import pytz

from app.utils.utils import StandardAlertLevels, get_lock_status


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

    def _lock_alert_type(self, level, text, evaluator):
        level = 'level_{}'.format(level)
        status = get_lock_status(self.config)

        if self.name not in status:
            status[self.name] = {}
        if level not in status[self.name]:
            status[self.name][level] = {}
        if evaluator not in status[self.name][level]:
            status[self.name][level][evaluator] = {}

        status[self.name][level][evaluator]['time'] = self.now.isoformat()
        status[self.name][level][evaluator]['text'] = text
        with open(self.config.lock_file, 'w+') as f:
            json.dump(status, f, indent=2)

    def _is_alert_locked(self, level, evaluator):
        logging.debug('checking: {} {} {}'.format(self.name, level, evaluator))
        level = 'level_{}'.format(level)
        if level == StandardAlertLevels.it:
            # always send IT alerts
            return False

        lock_duration = timedelta(**self.settings['alert_lock'])
        lock_expire = self.now - lock_duration
        try:
            status = get_lock_status(self.config)
            last_alert = status[self.name][level]
            last_alert = last_alert[evaluator]
            last_alert_time = dateutil.parser.parse(last_alert['time'])
            if lock_expire < last_alert_time:
                return True
            else:
                return False
        except (KeyError, JSONDecodeError):
            return False

    def _send_it_alert(self, text):
        self._send_alert(StandardAlertLevels.it, text, None)

    def _send_alert(self, level, text, evaluator):
        if self._is_alert_locked(level, evaluator):
            send_sms = False
        else:
            send_sms = True
            self._lock_alert_type(level, text, evaluator)

        self.manager.log_alert(level, text, send_sms)

    def _log_event(self, level, text):
        self.manager.log_event(level, text)

    def run(self):
        raise NotImplementedError

    def _check_data(self):
        raise NotImplementedError

    def _store_data(self):
        raise NotImplementedError
