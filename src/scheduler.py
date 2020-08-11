import datetime
import threading


class Scheduler():
    def __init__(self):
        self._sync_events = []
        self._fixed_events = []

    def remove_old_events(self):
        pass

    def sync_events(self, events, event_func):

        # Look for and remove events in local db but not on google calendar
        for s_event in self._sync_events:
            if not s_event in events:
                print("Removing event " + s_event)
                self._sync_events.remove(s_event)

        # Look for and add event on google calendar but not in local db
        for event in events:
            if not event in self._sync_events:
                self._sync_events.append(event)
                event_time = datetime.datetime.strptime(event, "%Y-%m-%d %H:%M:%S")
                delta_time = (event_time - datetime.datetime.now()).total_seconds()
                # Schedule event
                print("Sceduling an event at " + event)
                threading.Timer(delta_time, event_func, args=[event]).start()

    def schedule_event(self, time, event_func):
        time_str = time.strftime("%Y-%m-%d %H:%M:%S")

        found_event = False
        if time_str in self._fixed_events:
            found_event = True
        else:
            self._fixed_events.append(time_str)

        delta_time = (time - datetime.datetime.now()).total_seconds()

        if not found_event:
            threading.Timer(delta_time, event_func, args=[time_str]).start()
        else:
            print("Event already exists! Not adding.")

    def remove_event(self, event):
        if event in self._fixed_events:
            self._fixed_events.remove(event)