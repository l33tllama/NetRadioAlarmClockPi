import base64
import json

from flask import Flask, render_template
from flask import request
from flask_socketio import SocketIO
from flask_socketio import send, emit

app = Flask(__name__, static_folder="../static", template_folder="../templates")
socketio = SocketIO(app)

add_station_cb = None
get_stations_cb = None
set_current_station_cb = None
get_current_station_cb = None
update_station_name_cb = None
get_stream_playing_cb = None
play_stream_cb = None
stop_stream_cb = None
set_volume_cb = None
get_schedule_cb = None
save_schedule_cb = None
saved_schedule = None
alarm_running_queue = None

# Disable caching!
@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route('/')
def index():
    return render_template('index.html')


@app.route("/save_schedule")
def save_schedule():
    global saved_schedule
    schedule_b64_str = request.args.get("sched")
    schedule_str = base64.b64decode(schedule_b64_str).decode('ascii')
    schedule = json.loads(schedule_str)
    saved_schedule = schedule
    print(schedule)
    if callable(save_schedule_cb):
        save_schedule_cb(schedule)
        return "OK"
    else:
        return "ERR: save_schedule_cb not callable"

@app.route("/get_schedule")
def get_schedule():
    global saved_schedule
    schedule = saved_schedule
    sched_b64_str = base64.b64encode(json.dumps(schedule).encode('ascii')).decode('ascii')
    return sched_b64_str

@app.route("/add_station")
def add_station():
    station_b64 = request.args.get('station_b64')
    station_url = base64.b64decode(station_b64).decode()
    if callable(add_station_cb):
        #print("Station URL: " + station_url)
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


@app.route("/update_station_name")
def update_station_name():
    station_b64 = request.args.get("station_b64")
    new_station_name_b64 = request.args.get("station_name_b64")
    station_url = base64.b64decode(station_b64).decode()
    new_station_name = base64.b64decode(new_station_name_b64).decode()
    if callable(update_station_name_cb):
        update_station_name_cb(station_url, new_station_name)
        return "OK"
    else:
        return "ERR: update_station_name_cb not callable"

@app.route("/get_status")
def get_status():
    return "OK"

@app.route("/start_radio")
def start_radio():
    global alarm_running_queue
    if callable(play_stream_cb):
        play_stream_cb(alarm_running_queue)
        return "OK"
    else:
        return "ERR: play_stream_cb not callable"

@app.route("/stop_radio")
def stop_radio():
    alarm_running_queue
    if callable(stop_stream_cb):
        stop_stream_cb(alarm_running_queue)
        return "OK"
    else:
        return "ERR: stop_stream_cb not callable"


@app.route("/set_volume")
def set_volume():
    global set_volume_cb
    volume = int(float(request.args.get("volume")))
    if callable(set_volume_cb):
        set_volume_cb(volume)
        return "OK"
    else:
        return "ERR: set_volume_cb not callable"


def emit_status(playing, volume, station_name):
    status_obj = {
        "playing": playing,
        "volume" : volume,
        "station_name" : station_name
    }
    socketio.emit("station-status", status_obj)


def run():
    #app.run(debug=True, host='0.0.0.0')
    socketio.run(app, host='0.0.0.0')