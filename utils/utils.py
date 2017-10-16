# -*- coding: utf-8 -*-
import json
import logging
import os
from json.decoder import JSONDecodeError

import yaml


def remove_duplicates(list_with_duplicates):
    no_duplicates = []
    for e in list_with_duplicates:
        if e not in no_duplicates:
            no_duplicates.append(e)
    return no_duplicates


def parse_yaml(path):
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


def files_in_dir(directory, file_filter=None):
    files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if file_filter is None or filename.endswith(file_filter):
                files.append(os.path.join(file_path))
    return sorted(files)


def get_latest_file(directory, file_filter):
    return files_in_dir(directory, file_filter)[-1]


def get_elem_text(xml, xpath):
    return xml.find(xpath).text


class StandardAlertLevels:
    it = -1
    no_alert = 0
    general = 1


class ApiStatuses:
    ok = [202]


def setup_logging(config):
    logging.basicConfig(filename=config.debug_log_file)
    logging.getLogger().addHandler(logging.StreamHandler())
    log_level = logging.getLevelName(config.log_level)
    logging.getLogger().setLevel(log_level)


def unix_time_millis(dt):
    return dt.timestamp() * 1000.0


def _get_lock_status(config):
    try:
        with open(config.lock_file) as lock_file:
            lock_status = json.load(lock_file)
    except JSONDecodeError:
        lock_status = {}

    return lock_status
