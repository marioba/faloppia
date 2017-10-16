import json
from random import randrange


def gen():
    items=[]
    for i in range(0, 432000, 600):
        t = i*1000 + 1507734000000
        val = randrange(0, 50)
        item = [t, val]
        items.append(item)
    return items

cpc={
    'accu_0060': {
        'rain': gen(),
        'past': gen()
    },
    'accu_0720': {
        'rain': gen(),
        'past': gen()
    }
}

prefix = 'cpc_values='
with open('/home/marco/dev/faloppia/data/cpc/latest.js', 'w') as f:
    f.write(prefix)
    json.dump(cpc, f)