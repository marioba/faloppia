# -*- coding: utf-8 -*-
import datetime
import logging
import os
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


def list_dir(directory):
    files = [f for f in os.listdir(directory) if os.path.isfile(f)]
    print(sorted(files))
    return files


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
