import datetime
from random import randint

import pytz

from config import Config
from web import CONFIG

CONFIG = Config()

# TODO REMOVE FAKE STUFF
CONFIG.set_fake_api_call()
FAKE_TEXTS = [
    'nothing special happening',
    'some rain coming',
    'heavy rain coming']
# END REMOVE FAKE STUFF


alert_level = randint(0, 2)
text = FAKE_TEXTS[alert_level]


def log_event(level, text):
    now = datetime.datetime.now(pytz.utc)
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    text = '{}, New alert level {}, {}\n'.format(now, level, text)
    with open(CONFIG.events_log_file, 'a') as f:
        f.write(text)


log_event(alert_level, text)
response = MessageSender(CONFIG).send_alert(alert_level, text)