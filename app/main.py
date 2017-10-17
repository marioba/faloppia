import json
import os

from flask.helpers import url_for
from json2html import *
from functools import wraps

# Flask stuff
from flask import (Flask,
                   render_template,
                   request,
                   Response,
                   send_from_directory)
from flask_bootstrap import Bootstrap
from flask_nav import Nav
from flask_nav.elements import Navbar, View

# Local stuff
from app.config import Config
from app.parsers_manager import ParsersManager
from app.utils.utils import setup_logging, files_in_dir, get_lock_status, \
    printable_time

# init application
app = Flask(__name__)
Bootstrap(app)
NAV = Nav()
NAV.init_app(app)
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
        View('Storia', 'history'),
    )


@app.route('/')
@requires_auth
def index():
    return render_template('index.html', config=CONFIG)


@app.route('/about')
@requires_auth
def about():
    items = []
    path = os.path.join(CONFIG.data_dir, 'static', 'informations')
    for f in files_in_dir(path, file_filter='.pdf', name_only=True):
        href = url_for(
            'data_file', filename='static/informations/{}'.format(f))

        name = f.replace("_", " ").replace("-", " ")[:-4]
        item = {'name': name, 'href': href}
        items.append(item)

    return render_template('about.html', config=CONFIG, items=items)


@app.route('/alerts')
@requires_auth
def alerts():
    alerts_file = get_lock_status(CONFIG)

    for k, v in alerts_file.items():
        for level_dict in v.values():
            for eval_dict in level_dict.values():
                eval_dict['time'] = printable_time(eval_dict['time'], CONFIG)
                eval_dict['messaggio'] = eval_dict.pop('text')
                eval_dict['orario messaggio'] = eval_dict.pop('time')

        for level, text in CONFIG.alert_text.items():
            try:
                clean_text = text
                clean_text = clean_text.replace(', {}', '')
                alerts_file[k][clean_text] = v.pop(level)
            except KeyError:
                pass


    table = json2html.convert(
        json=json.dumps(alerts_file, sort_keys=True),
        table_attributes='id="info-table" class="table table-bordered table-hover"')
    return render_template('alerts.html', config=CONFIG, table=table)


@app.route('/history')
@requires_auth
def history():
    log_file = CONFIG.events_log_file
    log = get_log(log_file)
    return render_template('log.html', config=CONFIG, log=log)


@app.route('/debug')
@requires_auth
def debug():
    log_file = CONFIG.debug_log_file
    log = get_log(log_file)
    return render_template('log.html', config=CONFIG, log=log)


@app.route('/parse')
@requires_auth
def parse():
    manager = ParsersManager(CONFIG)
    try:
        parsed = manager.run()
        content = str(parsed)
        code = 200
    except Exception as e:
        content = str(e)
        code = 500

    return content, code


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


@app.route('/data/<path:filename>')
@requires_auth
def data_file(filename):
    path = os.path.join(app.root_path, 'data')
    return send_from_directory(
        path,
        filename
    )


if __name__ == '__main__':
    # Only for debugging while developing
    app.run(host='127.0.0.1', debug=True, port=5000)

