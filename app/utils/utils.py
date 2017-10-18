# -*- coding: utf-8 -*-
import datetime
from logging import Formatter

import dateutil.parser
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
    try:
        with open(path, 'r') as stream:
            return yaml.safe_load(stream)
    except FileNotFoundError:
        return None


def files_in_dir(directory, file_filter=None, name_only=False):
    files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if file_filter is None or filename.endswith(file_filter):
                if name_only:
                    files.append(filename)
                else:
                    files.append(file_path)
    return sorted(files)


def get_latest_file(directory, file_filter):
    files = files_in_dir(directory, file_filter)
    try:
        return files[-1]
    except IndexError:
        return None


def get_elem_text(xml, xpath):
    return xml.find(xpath).text


class StandardAlertLevels:
    it = -1
    no_alert = 0
    general = 1


class ApiStatuses:
    ok = [202]


def setup_logging(config):
    fmt = '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    logging.basicConfig(filename=config.debug_log_file, format=fmt)
    logging.getLogger().addHandler(logging.StreamHandler())
    log_level = logging.getLevelName(config.log_level)
    logging.getLogger().setLevel(log_level)


def unix_time_millis(dt):
    return dt.timestamp() * 1000.0


def printable_time(value, config):
    if not isinstance(value, datetime.datetime):
        value = dateutil.parser.parse(value)

    return value.strftime(config.time_format)


def get_lock_status(config):
    try:
        with open(config.lock_file, 'r') as lock_file:
            lock_status = json.load(lock_file)
    except (JSONDecodeError, FileNotFoundError):
        lock_status = {}

    return lock_status
