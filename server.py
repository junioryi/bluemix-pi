from flask import Flask, redirect
from flask import render_template
from flask import request 
from flask import g, url_for, abort, flash

import sqlite3

import os, json
import ibmiotf.application
from contextlib import closing

# Configuration
DATABASE = './server.db'
DEBUG = True
SECRET_KEY = 'development key'

# Server env
try:
    vcap = json.loads(os.getenv("VCAP_SERVICES"))
    deviceId = os.getenv("DEVICE_ID")
except Exception :
    deviceId = "0000"


# Create the application
app = Flask(__name__)
app.config.from_object(__name__)
if os.getenv("VCAP_APP_PORT"):
    port = int(os.getenv("VCAP_APP_PORT"))
else:
    port = 5000

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text from entries order by id desc')
    entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    g.db.execute('insert into entries (title, text) values (?, ?)',
            [request.form['title'], request.form['text']])
    g.db.commit()
    flash('New entry was posted.')
    return redirect(url_for('show_entries'))

if __name__ == '__main__':
    if not os.path.isfile('server.db'):
        init_db()
    app.run(host='0.0.0.0', port=port)









