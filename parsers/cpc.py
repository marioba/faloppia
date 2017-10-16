import datetime
import dateutil.parser
import json
import os

import xml.etree.ElementTree as ET
from datetime import datetime

from parsers.base_parser import BaseParser
from utils.utils import unix_time_millis, get_latest_file


class CpcParser(BaseParser):
    def __init__(self, manager):
        super().__init__(manager)
        self.data = None

    def run(self):
        now_str = self._convert_datetime(self.now)
        start_str = self._convert_datetime(self.start)

        self._read_data()
        self._check_data()
        # self._store_data()

    def _read_data(self):
        latest_file = self._find_latest_xml()
        self.data = self._parse_xml(latest_file)

    def _find_latest_xml(self):
        return get_latest_file(self.settings['data_dir'], '.xml')

    def _parse_xml(self, filepath):

        tree = ET.parse(filepath)
        root = tree.getroot()
        accus = self.settings['accus']
        data = {}

        for name, value in accus.items():
            accu_data = self._parse_accu(root, name)
            data[name] = accu_data

        return data

    def _parse_accu(self, xml_root, accu_name):
        data = {}
        accu_format = "./ALERT[@accu='{}']".format(accu_name)
        alert = xml_root.find(accu_format)
        data['time'] = alert.find('./HEADER/time').text
        data['rain_measured'] = alert.find('./DATA/Region/sum_rain').text
        data['rain_forecast'] = alert.find('./DATA/Region/mean_rain').text
        data['rain'] = float(data['rain_measured']) + float(data['rain_forecast'])

        return data

    def _check_data(self):
        for name, data in self.data.items():
            thresholds = self.settings['accus'][name]['thresholds']
            for alert_level, ts in thresholds.items():
                alert_level = int(alert_level.split('_')[-1])
                for value, text in ts:
                    evaluation = value.format(data['rain'])
                    if eval(evaluation):
                        text = text.format(
                            data['rain'], data['time'])
                        text = '{} - {}'.format(self.name, text)
                        self._send_alert(alert_level, text)

    def _store_data(self):
        js_data = []
        for point in self.data:
            timestamp = unix_time_millis(self._convert_datetime(point[0]))
            try:
                value = float(point[1])
            except ValueError:
                value = None
            js_data.append([timestamp, value])
        initial_time = self._convert_datetime(self.data[0][0])
        initial_time = unix_time_millis(initial_time)
        file_path = os.path.join(self.config.data_dir, self.name, 'latest.js')
        with open(file_path, 'w') as f:
            f.write('oasi_min_value={}\noasi_values='.format(initial_time))
            json.dump(js_data, f)

    @staticmethod
    def _convert_datetime(value):
        # '2017-10-11T01:30:00+02:00'
        fmt = '%Y-%m-%dT%H:%M:%S%z'
        if isinstance(value, datetime):
            return value.strftime(fmt)

        return dateutil.parser.parse(value)

