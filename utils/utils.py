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


class StandardAlertLevels:
    it = -1
    no_alert = 0
    general = 1


class ApiStatuses:
    ok = [202]
