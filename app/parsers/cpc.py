import datetime
import json
import os
import logging

import xml.etree.ElementTree as ET

import pytz

from app.parsers.base_parser import BaseParser
from app.utils.message_sender import FatalError
from app.utils.utils import get_latest_file, get_elem_text, printable_time


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
        if latest_file is None:
            raise FatalError('No CPC XML file found')

        latest_file_date = self._get_file_date(latest_file)
        allowed_delay = self.settings['data_update_freq']
        allowed_delay = datetime.timedelta(minutes=allowed_delay)
        delay = self.now - latest_file_date

        if delay > allowed_delay:
            message = 'The last CPC file is {} old ({})'.format(
                delay, latest_file_date)
            self._send_it_alert(message)
        self.data = self._parse_xml(latest_file)

    @staticmethod
    def _get_file_date(latest_file):
        file_date = str(latest_file[:-4].split('VRAA71.')[1])
        fmt = "%Y%m%d%H%M"
        file_date = datetime.datetime.strptime(file_date, fmt)
        file_date = pytz.utc.localize(file_date)
        return file_date

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
                logging.debug(text)
                continue
            if data['rain'] is None:
                continue

            thresholds = self.settings['accus'][name]['thresholds']
            for alert_level, ts in thresholds.items():
                alert_level = int(alert_level.split('_')[-1])
                for evaluator, text in ts:
                    evaluation = evaluator.format(data['rain'])
                    if eval(evaluation):
                        time = datetime.datetime.fromtimestamp(
                            data['time']/1000)
                        time = printable_time(time, self.config)
                        text = text.format(data['rain'], time)
                        text = '{} - {}'.format(self.name, text)
                        self._send_alert(alert_level, text, evaluator)

    def _store_data(self):
        prefix = 'cpc_values='
        file_path = os.path.join(self.config.data_dir, self.name, 'latest.js')
        try:
            with open(file_path, 'r') as f:
                data = f.read()
                current_data = json.loads(data[len(prefix):])
        except FileNotFoundError:
            current_data = {}

        max_values = self.timespan.days * 24 * 60 / self.settings[
            'data_update_freq']
        for accu, data in self.data.items():
            if accu not in current_data:
                current_data[accu] = {'rain': [], 'past': []}
            for name in ['rain', 'past']:
                data_list = current_data[accu][name]
                if len(data_list) > max_values:
                    cut = int(len(data_list) - max_values)
                    del data_list[0:cut]
                data_list.append([data['time'], data[name]])

        with open(file_path, 'w+') as f:
            f.write(prefix)
            json.dump(current_data, f, sort_keys=True, indent=2)
