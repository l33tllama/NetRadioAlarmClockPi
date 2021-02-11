import datetime
import threading

class Scheduler():
    def __init__(self):
        self._fixed_events = []

    # Add an event if not exists
    def add_event(self, time, cb_func):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        event_found = False
        for event in self._fixed_events:
            if time.strptime(event["time"], "%Y-%m-%d %H:%M:%S") == time_str:
                event_found = True
        if not event_found:
            self._fixed_events.append({"time": time, "cb_func": cb_func})

    def process_events(self):
        cur_time = datetime.datetime.now()
        for event in self._fixed_events:
            e_time = event["time"]
            if e_time.hour == cur_time.hour and \
                e_time.min == cur_time.min and \
                    e_time.weekday() == cur_time.weekday():
                if callable(e_time["cb_func"]):
                    e_time["cb_func"]()

    def remove_all_events(self):
        self._fixed_events.clear()