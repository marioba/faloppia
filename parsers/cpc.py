import datetime
import dateutil.parser
import json
import os

import xml.etree.ElementTree as ET
from datetime import datetime

from parsers.base_parser import BaseParser
from utils.utils import unix_time_millis, get_latest_file, get_elem_text, \
    StandardAlertLevels


class CpcParser(BaseParser):
    def __init__(self, manager):
        super().__init__(manager)
        self.data = None

    def run(self):
        self._read_data()
        self._check_data()
        self._store_data()

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
        """
        In assenza di precipitazioni il modulo statistico NON viene fatto
        partire e alcuni campi nel file XML sono assenti
        Nella sezione <DATA> dei files presenti nel ZIP file mancano i campi:
        - test_stat :  precipitazione (passato + futuro)  è campo da utilizzare
        per le allerte
        - perc_past_R : % di precipitazione (campo test_stat) caduta nel
        passato
        - plausibility_reg_rain :  test di plausibilità, se 0 NON utilizzare
        per inviare allerte


        :param xml_root:
        :param accu_name:
        :return:
        """
        data = {}
        accu_format = "./ALERT[@accu='{}']".format(accu_name)
        alert = xml_root.find(accu_format)

        data['time'] = int(get_elem_text(alert, './HEADER/seconds')) * 1000
        data_section = "./DATA/Region[@ID='{}']".format(
            self.settings['accus'][accu_name]['region'])
        data_section = alert.find(data_section)

        try:
            rain = get_elem_text(data_section, 'test_stat')
            percent = get_elem_text(data_section, 'perc_past_R')
            past = float(rain) * float(percent) / 100.0
            plausibility = get_elem_text(data_section, 'plausibility_reg_rain')
        except AttributeError:
            rain = None
            past = None
            plausibility = None

        data['rain'] = rain
        data['past'] = past
        data['plausibility'] = plausibility
        return data

    def _check_data(self):
        for name, data in self.data.items():
            if data['plausibility'] == 0:
                data['rain'] = None
                data['past'] = None
                text = 'Plausibility 0 found, skipping'
                self._log_event(StandardAlertLevels.it, text)
                continue
            if data['rain'] is None:
                continue

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
        prefix = 'cpc_values='
        file_path = os.path.join(self.config.data_dir, self.name, 'latest.js')
        with open(file_path, 'r') as f:
            data = f.read()
            js_data = json.loads(data[len(prefix):])

        cpc_update_freq = 10  # min
        max_values = self.timespan.days * 24 * 60 / cpc_update_freq
        for accu, data in self.data.items():
            for name in ['rain', 'past']:
                data_list = js_data[accu][name]
                if len(data_list) > max_values:
                    cut = int(len(data_list) - max_values)
                    del data_list[0:cut]
                data_list.append([data['time'], data[name]])

        with open(file_path, 'w') as f:
            f.write(prefix)
            json.dump(js_data, f)
