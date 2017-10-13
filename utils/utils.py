# -*- coding: utf-8 -*-

import datetime
import pytz
import yaml


def parse_yaml(path):
    with open(path, 'r') as stream:
        return yaml.safe_load(stream)


def remove_duplicates(list_with_duplicates):
    no_duplicates = []
    for e in list_with_duplicates:
        if e not in no_duplicates:
            no_duplicates.append(e)
    return no_duplicates


def log_event(level, text):
    now = datetime.datetime.now(pytz.utc)
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    text = '{}, New alert level {}, {}\n'.format(now, level, text)
    with open('/home/marco/dev/faloppia/logs/river_warn_events.log', 'a') as f:
        f.write(text)


class StandardAlertLevels:
    it = -1
    no_alert = 0
    general = 1


class ApiStatuses:
    ok = [202]
