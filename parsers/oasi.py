import json
import urllib.request

from datetime import timedelta

from parsers.base_parser import BaseParser


class OasiParser(BaseParser):
    def __init__(self, manager):
        super().__init__(manager)
        self.data = None

    def run(self):
        yesterday = self.now - timedelta(self.settings['timespan'])
        now = self._format_datetime(self.now)
        yesterday = self._format_datetime(yesterday)

        timespan = '{}/{}'.format(yesterday, now)
        url = 'https://geoservice.ist.supsi.ch/psos/sos?service=SOS&version=1.0.0&request=GetObservation&offering=temporary&procedure=Q_FAL_CHIA&observedProperty=urn:ogc:def:parameter:x-istsos:1.0:river:water:discharge&responseFormat=application/json&eventTime={}'.format(timespan)
        with urllib.request.urlopen(url) as url:
            data = json.loads(url.read().decode())
            data = data['ObservationCollection']['member'][0]
            self.data = data['result']['DataArray']['values']
        self.check_data()

    def check_data(self):
        last_time, last_value = self.data[-1]
        last_value = 6.001
        thresholds = self.settings['thresholds']
        for alert_level, ts in thresholds.items():
            alert_level = int(alert_level.split('_')[-1])
            for value, text in ts:
                evaluation = value.format(last_value)
                if eval(evaluation):
                    text = text.format(last_value, last_time)
                    text = '{} - {}'.format(self.name, text)
                    self._send_alert(alert_level, text)

    @staticmethod
    def _format_datetime(datetime):
        return datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
