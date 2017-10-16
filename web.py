import os
from json2html import *
from functools import wraps

# Flask stuff
from flask import (Flask,
                   render_template,
                   request,
                   Response,
                   send_from_directory, redirect)
from flask.helpers import url_for
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View

# Local stuff
from config import Config
from parsers_manager import ParsersManager
from utils.utils import setup_logging

# init application
APP = Flask(__name__)
Bootstrap(APP)
NAV = Nav()
NAV.init_app(APP)
CONFIG = Config()
setup_logging(CONFIG)


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


@NAV.navigation()
def navigation_bar():
    return Navbar(
        CONFIG.app_name,
        View('Situazione', 'index'),
        View('Allerte attive', 'alerts'),
        View('Informazioni', 'about'),
        View('Aggiorna', 'parse'),
        View('Storia', 'history'),
        View('Debug', 'debug'),
    )


@APP.route('/')
@requires_auth
def index():
    return render_template('index.html', config=CONFIG)


@APP.route('/about')
@requires_auth
def about():
    return render_template('about.html', config=CONFIG)


@APP.route('/alerts')
@requires_auth
def alerts():
    log_file = CONFIG.lock_file
    log = get_log(log_file)
    table = json2html.convert(
        json=log, table_attributes="id=\"info-table\" class=\"table table-bordered table-hover\"")
    return render_template('alerts.html', config=CONFIG, table=table)


@APP.route('/history')
@requires_auth
def history():
    log_file = CONFIG.events_log_file
    log = get_log(log_file)
    return render_template('log.html', config=CONFIG, log=log)


@APP.route('/debug')
@requires_auth
def debug():
    log_file = CONFIG.debug_log_file
    log = get_log(log_file)
    return render_template('log.html', config=CONFIG, log=log)


def get_log(log_file):
    empty_log = 'No events recorded yet'
    try:
        with open(log_file, 'r') as f:
            log = f.read()
            if not log:
                log = empty_log
    except FileNotFoundError:
        log = empty_log
    return log


@APP.route('/parse')
@requires_auth
def parse():
    manager = ParsersManager(CONFIG)
    manager.run()
    return redirect(url_for('index'))


@APP.route('/data/<path:filename>')
@requires_auth
def data_file(filename):
    path = os.path.join(APP.root_path, 'data')
    return send_from_directory(
        path,
        filename
    )


if __name__ == '__main__':
    APP.run()
