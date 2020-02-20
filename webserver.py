import base64
import json

from flask import Flask, render_template
from flask import request

app = Flask(__name__, static_folder="static")

add_station_cb = None
get_stations_cb = None

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/add_station")
def add_station():
    station_b64 = request.args.get('station_b64')
    station_url = base64.decode(station_b64).decode()
    if callable(add_station_cb):
        add_station_cb(station_url)


@app.route("/get_stations")
def get_stations():
    if callable(get_stations_cb):
        stations = get_stations_cb()
        return json.dumps(stations)
    else:
        return "ERR: get_stations_cb not callable"

def run():
    app.run(debug=True, host='0.0.0.0')