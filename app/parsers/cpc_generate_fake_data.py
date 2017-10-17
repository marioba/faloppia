import json
from random import randrange


def gen():
    items = {
        'short_rain': [],
        'short_past': [],
        'long_rain': [],
        'long_past': [],
    }
    for i in range(0, 432000, 600):
        t = i*1000 + 1507734000000
        short_val = randrange(0, 50)
        long_val = short_val * randrange(100, 500) / 100.0
        past = randrange(0, 100) / 100.0
        for k, v in items.items():
            if k == 'short_rain':
                val = short_val
            elif k == 'short_past':
                val = short_val * past
            elif k == 'long_rain':
                val = long_val
            elif k == 'long_past':
                val = long_val * past
            v.append([t, val])
    return items


data = gen()


cpc = {
    'accu_0060': {
        'rain': data['short_rain'],
        'past': data['short_past']
    },
    'accu_0720': {
        'rain': data['long_rain'],
        'past': data['long_past']
    }
}

prefix = 'cpc_values='
with open('/home/marco/dev/faloppia/app/data/cpc/latest.js', 'w+') as f:
    f.write(prefix)
    json.dump(cpc, f, sort_keys=True, indent=2)
