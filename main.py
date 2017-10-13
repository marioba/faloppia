import logging
import json

from flask import Flask


from config import Config
from utils.message_sender import MessageSender

CONFIG = Config()

logging.basicConfig(filename=CONFIG.log_file)
logging.getLogger().addHandler(logging.StreamHandler())
log_level = logging.getLevelName(CONFIG.log_level)
logging.getLogger().setLevel(log_level)

app = Flask(__name__)


@app.route('/')
def main():
    text = CONFIG.alert_text.format('http://berna.io')
    alert_level = 3
    params, response = MessageSender(CONFIG).send_alert(alert_level, text)
    print(type(response))
    print(response)
    #parsed = json.loads(response)

    return "1"#json.dumps(parsed, indent=4, sort_keys=True)


if __name__ == '__main__':
    app.run()
