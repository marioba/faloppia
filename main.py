import datetime
import logging
import os
from random import randint
from functools import wraps


# Flask stuff
import pytz
from flask import request, Response, send_from_directory
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View


# Local stuff
from config import Config
from utils.message_sender import MessageSender

app = Flask(__name__)
Bootstrap(app)
nav = Nav()
nav.init_app(app)

CONFIG = Config(app.root_path)

# TODO REMOVE FAKE STUFF
CONFIG.set_fake_api_call()
FAKE_TEXTS = [
    'nothing special happening',
    'some rain coming',
    'heavy rain coming']
# END REMOVE FAKE STUFF


logging.basicConfig(filename=CONFIG.debug_log_file)
logging.getLogger().addHandler(logging.StreamHandler())
log_level = logging.getLevelName(CONFIG.log_level)
logging.getLogger().setLevel(log_level)


def check_auth(username, password, config):
    """This function is called to check if a username /
    password combination is valid.
    :param config:
    """
    return username == config.username and password == config.password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password, CONFIG):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@nav.navigation()
def navigation_bar():
    return Navbar(
        CONFIG.app_name,
        View('Status', 'index'),
        View('History', 'history'),
        View('About', 'about'),
    )


@app.route('/')
@requires_auth
def index():
    alert_level = randint(0, 2)
    text = FAKE_TEXTS[alert_level]

    log_event(alert_level, text)
    response = MessageSender(CONFIG).send_alert(alert_level, text)

    return render_template('index.html', config=CONFIG)


@app.route('/about')
@requires_auth
def about():
    return render_template('about.html', config=CONFIG)


@app.route('/history')
@requires_auth
def history():
    try:
        with open(CONFIG.events_log_file, 'r') as f:
            log = f.read()
    except FileNotFoundError:
        log = 'No events recorded yet'
    return render_template('history.html', config=CONFIG, log=log)


@app.route('/data/<path:directory>/<path:filename>')
@requires_auth
def data_file(directory, filename):
    path = os.path.join(app.root_path, 'data', directory)
    return send_from_directory(
        path,
        filename
    )


def log_event(level, text):
    now = datetime.datetime.now(pytz.utc)
    now = now.strftime('%Y-%m-%d %H:%M:%S')
    text = '{}, New alert level {}, {}\n'.format(now, level, text)
    with open(CONFIG.events_log_file, 'a') as f:
        f.write(text)


if __name__ == '__main__':
    app.run()