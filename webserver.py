import base64
import json

from flask import Flask, render_template
from flask import request

app = Flask(__name__, static_folder="static")

add_station_cb = None
get_stations_cb = None
set_current_station_cb = None
get_current_station_cb = None

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/add_station")
def add_station():
    station_b64 = request.args.get('station_b64')
    station_url = base64.b64decode(station_b64).decode()
    if callable(add_station_cb):
        add_station_cb(station_url)
        return "OK"
    else:
        return "ERR: add_station_cb not callable"


@app.route("/get_stations")
def get_stations():
    if callable(get_stations_cb):
        stations = get_stations_cb()
        return json.dumps(stations)
    else:
        return "ERR: get_stations_cb not callable"

@app.route("/set_current_station")
def set_current_station():
    if callable(set_current_station_cb):
        station_b64 = request.args.get('station_b64')
        station_url = base64.b64decode(station_b64).decode()
        set_current_station_cb(station_url)
        return "OK"
    else:
        return "ERR: set_current_station_cb not callable"


@app.route("/get_current_station")
def get_current_station():
    if callable(get_current_station_cb):
        station, title = get_current_station_cb()
        return json.dumps([station, title])
    else:
        return "ERR: get_current_station_cb not callable"


def run():
    app.run(debug=True, host='0.0.0.0')