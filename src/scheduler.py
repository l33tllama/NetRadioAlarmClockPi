import datetime
import threading

class Scheduler():
    def __init__(self):
        self._fixed_events = []
        self._daily_events = []
        self.current_alarm_tuple = (-1, -1, -1)

    # Add an event if not exists
    def add_event(self, time, cb_func):
        print("Adding new event " + str(time))
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")
        event_found = False
        for event in self._fixed_events:
            if event["time"].strftime("%Y-%m-%d %H:%M:%S") == time_str:
                event_found = True
        if not event_found:
            self._fixed_events.append({"time": time, "cb_func": cb_func})

    def add_weekday_event_day(self, day, time, cb_func):
        event_found = False
        for event in self._daily_events:
            if event["day"] == day and datetime.datetime.strftime(event["time"], "%H:%M") == time:
                event_found = True
        if not event_found:
            self._daily_events.append({"day" : day, "time" : time, "cb_func" : cb_func})

    def process_events(self):
        cur_time = datetime.datetime.now()

        # Specific time events (testing and maybe todo ???)
        for event in self._fixed_events:
            e_time = event["time"]
            e_str = "{0}, {1}, {2}".format(e_time.hour, e_time.minute, e_time.weekday())
            cur_str = "{0}, {1}, {2}".format(cur_time.hour, cur_time.minute, cur_time.weekday())
            print("event: " + e_str + " - cur " + cur_str)
            cur_tuple = (cur_time.hour, cur_time.minute, cur_time.weekday())
            if e_time.hour == cur_time.hour and \
                e_time.minute == cur_time.minute and \
                    e_time.weekday() == cur_time.weekday() and \
                        not cur_tuple == self.current_alarm_tuple:
                self.current_alarm_tuple = (e_time.hour, e_time.minute, e_time.weekday())
                print("(trying to) Calling schedule event!!")
                cb_func = event["cb_func"]
                if callable(cb_func):
                    cb_func()
                else:
                    print("schedule cb_func not callable!")

        # Day of week events (taken from web interface)
        for event in self._daily_events:
            e_time = event["time"]
            e_dow = event["day"]
            cur_tuple = (cur_time.hour, cur_time.minute, cur_time.weekday())
            if e_dow == cur_tuple[2]:
                print("Event on day " + str(e_dow) + " time " + str(e_time))
            if e_time.hour == cur_time.hour and \
                e_time.minute == cur_time.minute and \
                    e_dow == cur_time.weekday() and \
                        not cur_tuple == self.current_alarm_tuple:
                self.current_alarm_tuple = (e_time.hour, e_time.minute, e_dow)
                print("(trying to) Calling schedule weekday event!!")
                cb_func = event["cb_func"]
                if callable(cb_func):
                    cb_func()
                else:
                    print("schedule cb_func not callable!")

    def remove_all_events(self):
        self._fixed_events.clear()
        self._daily_events.clear()