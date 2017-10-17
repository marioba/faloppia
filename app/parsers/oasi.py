import datetime
import dateutil.parser
import json
import os
import urllib.request

from datetime import datetime

from app.parsers.base_parser import BaseParser
from app.utils.utils import unix_time_millis


class OasiParser(BaseParser):
    def __init__(self, manager):
        super().__init__(manager)
        self.data = None

    def run(self):
        now_str = self._convert_datetime(self.now)
        start_str = self._convert_datetime(self.start)

        timespan = '{}/{}'.format(start_str, now_str)
        url = 'https://geoservice.ist.supsi.ch/psos/sos?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&procedure=Q_FAL_CHIA&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:river:water:discharge&responseFormat=application/json&eventTime={}'.format(timespan)
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
            data = data['ObservationCollection']['member'][0]
            self.data = data['result']['DataArray']['values']
        self._check_data()
        self._store_data()

    def _check_data(self):
        last_time, last_value = self.data[-1]
        thresholds = self.settings['thresholds']
        for alert_level, ts in thresholds.items():
            alert_level = int(alert_level.split('_')[-1])
            for evaluator, text in ts:
                evaluation = evaluator.format(last_value)
                if eval(evaluation):
                    time = self._convert_datetime(last_time)
                    time = time.strftime(self.config.time_format)
                    text = text.format(last_value, time)
                    text = '{} - {}'.format(self.name, text)

                    self._send_alert(alert_level, text, evaluator)

    def _store_data(self):
        js_data = []
        for point in self.data:
            timestamp = unix_time_millis(self._convert_datetime(point[0]))
            try:
                value = float(point[1])
            except ValueError:
                value = None
            js_data.append([timestamp, value])
        file_path = os.path.join(self.settings['data_dir'], 'latest.js')
        with open(file_path, 'w') as f:
            f.write('oasi_values=')
            json.dump(js_data, f, sort_keys=True, indent=2)

    @staticmethod
    def _convert_datetime(value):
        # '2017-10-11T01:30:00+02:00'
        fmt = '%Y-%m-%dT%H:%M:%S%z'
        if isinstance(value, datetime):
            return value.strftime(fmt)

        return dateutil.parser.parse(value)

