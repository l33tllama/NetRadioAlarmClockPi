import time
import threading
import datetime

from multimedia_controller import MultimmediaController
from rpi_gpio import RPiGPIO
from scheduler import Scheduler
import webserver
import sys
from radio_db import RadioDB
from arduino_controller import ArduinoController

radio_triplej_url = "http://www.abc.net.au/res/streaming/audio/mp3/triplej.pls"

i2c_lock = False

class NetRadioAlarmClock():
    def __init__(self):
        self.media = MultimmediaController()
        self.sched = Scheduler()
        self.schedule = {}
        #self.gcal = GoogleCalendar()
        self.arduino = ArduinoController(0x08)
        self.gpio = RPiGPIO()
        self.radio_db = RadioDB("/home/pi/Python/NetRadioAlarmClockPi/radio-settings.db")
        self.webserver = webserver
        self.webserver.add_station_cb = self.add_station
        self.webserver.get_stations_cb = self.radio_db.get_stations
        self.webserver.set_current_station_cb = self.set_current_station
        self.webserver.get_current_station_cb = self.get_current_station
        self.webserver.update_station_name_cb = self.radio_db.update_station_title
        self.webserver.get_stream_playing_cb = self.media.get_playing
        self.webserver.play_stream_cb = self.start_stream
        self.webserver.stop_stream_cb = self.stop_stream
        self.webserver.set_volume_cb = self.media.set_volume
        self.webserver.get_schedule_cb = self.get_schedule
        self.webserver.save_schedule_cb = self.save_schedule
        self.alarm_running = False
        self.update_interval = 60 * 5
        self.state = "idle"
        self.gpio.set_snooze_btn_callback(self.alarm_snooze_event)
        self.webdev = False
        self.stream_playing = False

        # Set current station
        url, station_title = self.get_current_station()
        self.media.set_stream_url(url)

        # Load radio alarm schedule and set up events if there are any
        self.load_schedule()
        self.create_events()

        # Test event
        test_time = datetime.datetime(2021, 2, 23, 20, 14, 0)
        self.sched.add_event(test_time, self.alarm_event)

        if len(sys.argv) > 0:
            #print(sys.argv)
            if sys.argv[1].replace("\r","") == "webdev":
                print("Web development mode")
                self.webdev = True

        if not self.webdev:
            print("Resetting Arduino")
            self.gpio.reset_arduino()
            print("Done")

            self.arduino.set_vol_change_callback(self.media.set_volume)
            self.arduino.start_rot_enc_thread()

    # Set current station from web interface
    def set_current_station(self, station_url):
        self.radio_db.set_current_station(station_url)
        self.media.set_stream_url(station_url)

    def add_station(self, station_url):
        title = self.media.get_title_from_any_url(station_url)
        self.radio_db.add_station(station_url, title)

    def get_current_station(self):
        station_url = self.radio_db.get_current_station()
        title = self.radio_db.get_title_for_station_url(station_url)
        return station_url, title

    def test_radio(self):
        self.media.set_stream_url(radio_triplej_url)
        self.media.play_stream()

    def test_alarm(self):
        pass

    def start_stream(self):
        self.media.play_stream()
        self.stream_playing = True
        volume = self.media.get_volume()
        url, station_name = self.get_current_station()
        self.webserver.emit_status(self.stream_playing, volume, station_name)

    def stop_stream(self):
        self.media.stop_stream()
        self.stream_playing = False
        volume = self.media.get_volume()
        url, station_name = self.get_current_station()
        webserver.emit_status(self.stream_playing, volume, station_name)

    def setup(self):
        #print("Station: " + self.mpdc.get_station_name())
        #print("Artist: " + self.mpdc.get_artist())
        #print("Title: " + self.mpdc.get_title())

        if not self.webdev:
            # display idle screen
            self.arduino.update_lcd_idle()

            # read events from google calendar
            self.update_events("null")
            self.media.set_stream_url(radio_triplej_url)

            # Testing
            #self.test_radio()
            #self.alarm_event(datetime.datetime.now())

        # update time on arduino
        #self.update_lcd_idle("null")

    def get_schedule(self):
        events = self.radio_db.get_events()
        cur_time = datetime.datetime.now()
        schedule = {
            "weekday_time": "",
            "enabled_weekdays": [],
            "weekend_time": "",
            "enabled_weekend_days": [],
            "next_alarm": ""
        }
        for event in events:
            e_time = datetime.datetime.strptime(event, "%Y-%m-%d %H:%M:%S")
            if (e_time - cur_time).hours < 24:
                schedule["next_alarm"] = event
            if e_time.weekday() >=0 and e_time.weekday() < 5:
                schedule["weekday_time"] = event
            if e_time.weekday() >=5 and e_time.weekday() < 7:
                schedule["weekend_time"] = event
            if e_time.weekday() == 0:
                schedule["enabled_weekdays"].append("monday")
            if e_time.weekday() == 1:
                schedule["enabled_weekdays"].append("tuesday")
            if e_time.weekday() == 2:
                schedule["enabled_weekdays"].append("wednesday")
            if e_time.weekday() == 3:
                schedule["enabled_weekdays"].append("thursday")
            if e_time.weekday() == 4:
                schedule["enabled_weekdays"].append("friday")
            if e_time.weekday() == 5:
                schedule["enabled_weekend_days"].append("saturday")
            if e_time.weekday() == 6:
                schedule["enabled_weekend_days"].append("sunday")

    def save_schedule(self, schedule):
        print("Saving new schedule?")
        self.schedule = schedule
        self.radio_db.save_schedule(schedule)
        self.create_events()

    def load_schedule(self):
        self.schedule = self.radio_db.load_schedule()
        self.webserver.saved_schedule = self.schedule
        print("Saved schedule: " + str(self.schedule))

    def create_events(self):

        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        if self.schedule is None:
            return
        enabled_weekdays = self.schedule["enabled_weekdays"]
        enabled_weekend_days = self.schedule["enabled_weekend_days"]
        weekday_time = datetime.datetime.strptime(self.schedule["weekday_time"], "%H:%M")
        weekend_time = datetime.datetime.strptime(self.schedule["weekend_time"], "%H:%M")

        def get_day_integer(day_str):
            for i in range(0, len(days)):
                day_i_str = days[i]
                if day_i_str == day_str:
                    return i
            print("ERROR: No day for : '" + day_str + "'")
            return -1

        self.sched.remove_all_events()

        for day in enabled_weekdays:
            day_int = get_day_integer(day)
            if day_int >= 0:
                print("Adding alarm for day: " + days[day_int])
                self.sched.add_weekday_event_day(day_int, weekday_time, self.alarm_event)
            else:
                print("ERROR: weekday int not found for '" + day +"', " + str(day_int))

        for day in enabled_weekend_days:
            day_int = get_day_integer(day)
            if day_int > 0:
                print("Adding alarm for weekend day: " + days[day_int])
                self.sched.add_weekday_event_day(day_int, weekend_time, self.alarm_event)
            else:
                print("ERROR: weekend day int not found for '" + day + "'")

    def add_events_new(self, events, cb_func):
        self.radio_db.clear_events()
        self.sched.remove_all_events()
        for event in events:
            self.radio_db.add_event(event["time"])
            self.sched.add_event(event["time"], cb_func)

    def update_lcd_playing(self, time_str):
        #station = self.mpdc.get_station_name()
        #artist = self.mpdc.get_artist()
        #title = self.mpdc.get_title()

        station = self.media.get_station_title()

        print("station: " + station)

        self.arduino.update_lcd_playing(station, "", "")

        one_second = datetime.datetime.now() + datetime.timedelta(seconds=1)
        
        if self.state == "playing":
            self.sched.schedule_event(one_second, self.update_lcd_playing)

    
    def update_lcd_idle(self, time_str):
        self.arduino.update_lcd_idle()
        one_second = datetime.datetime.now() + datetime.timedelta(seconds=1)
        
        if self.state == "idle":
            self.sched.schedule_event(one_second, self.update_lcd_idle)

    def alarm_snooze_event(self, channel):
        self.state = "idle"
        self.media.stop_stream()
        self.alarm_running = False
        if not self.webdev:
            self.update_lcd_idle("null")

    def alarm_event(self):
        self.state = "playing"
        self.media.play_stream()
        self.alarm_running = True
        if not self.webdev:
            self.update_lcd_playing("null")
        print("woop")
        pass

    def run_alarm_button(self):
        while True:
            self.sched.process_events()
            time.sleep(3)
            if self.alarm_running:
                self.gpio.snooze_button_led_on()
                time.sleep(0.5)
                self.gpio.snooze_button_lef_off()
                time.sleep(0.5)

    def run(self):
        alarm_btn_thread = threading.Thread(target=self.run_alarm_button)
        alarm_btn_thread.daemon = True
        alarm_btn_thread.start()
        self.webserver.run()



if __name__ == "__main__":
    print("Start.")
    clock = NetRadioAlarmClock()
    clock.setup()
    clock.run()
    print("Running")