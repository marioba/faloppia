import logging

# Flask stuff
from flask import Flask, render_template

from flask_bootstrap import Bootstrap

from flask_nav import Nav
from flask_nav.elements import Navbar, View

# Local stuff
from config import Config
from utils.message_sender import MessageSender


CONFIG = Config()
CONFIG.set_fake_api_call()

logging.basicConfig(filename=CONFIG.debug_log_file)
logging.getLogger().addHandler(logging.StreamHandler())
log_level = logging.getLevelName(CONFIG.log_level)
logging.getLogger().setLevel(log_level)


app = Flask(__name__)
Bootstrap(app)
nav = Nav()
nav.init_app(app)

@nav.navigation()
def navigation_bar():
    return Navbar(
        CONFIG.app_name,
        View('Status', 'index'),
        View('History', 'history'),
        View('About', 'about'),
    )


@app.route('/')
def index():
    text = 'heavy rain coming'
    alert_level = 2
    response = MessageSender(CONFIG).send_alert(alert_level, text)

    return render_template('index.html', config=CONFIG, response=response)


@app.route('/about')
def about():
    return render_template('about.html', config=CONFIG)


@app.route('/history')
def history():
    with open(CONFIG.events_log_file, 'r') as f:
        log = f.read()
    return render_template('history.html', config=CONFIG, log=log)


if __name__ == '__main__':
    app.run()
