import csv
import re
import os
import sqlite3 as sql

from flask import *
from werkzeug.utils import secure_filename
import hashlib

from routes import dashboard, users
import config

UPLOAD_FOLDER = 'csv/'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = config.SECRET

app.register_blueprint(dashboard.blueprint, url_prefix='/dashboard')
app.register_blueprint(users.blueprint, url_prefix='/users')

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username', None))

@app.route('/static/<path>', methods=['GET'])
def serve_static(path):
    return send_from_directory('./static/', path)

if __name__ == "__main__":
    app.run(debug = True, host='0.0.0.0', port=5005)
