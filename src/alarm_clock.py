import time
import threading
import datetime

from google_calendar import GoogleCalendar
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
        #self.mpdc = MPDController()
        self.media = MultimmediaController()
        self.sched = Scheduler()
        #self.gcal = GoogleCalendar()
        self.arduino = ArduinoController(0x08)
        self.gpio = RPiGPIO()
        self.radio_db = RadioDB("../radio-settings.db")
        self.webserver = webserver
        self.webserver.add_station_cb = self.add_station
        self.webserver.get_stations_cb = self.radio_db.get_stations
        self.webserver.set_current_station_cb = self.radio_db.set_current_station
        self.webserver.get_current_station_cb = self.get_current_station
        self.webserver.update_station_name_cb = self.radio_db.update_station_title
        self.webserver.get_stream_playing_cb = self.media.get_playing
        self.alarm_running = False
        self.update_interval = 60 * 5
        self.state = "idle"
        self.gpio.set_snooze_btn_callback(self.alarm_snooze_event)
        self.webdev = False

        if len(sys.argv) > 1:
            if sys.argv[1] == "webdev":
                self.webdev = True

        if not self.webdev:
            print("Resetting Arduino")
            self.gpio.reset_arduino()
            print("Done")

            self.arduino.set_vol_change_callback(self.media.set_volume)
            self.arduino.start_rot_enc_thread()

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

    def setup(self):
        #print("Station: " + self.mpdc.get_station_name())
        #print("Artist: " + self.mpdc.get_artist())
        #print("Title: " + self.mpdc.get_title())

        if not self.webdev:
            # display idle screen
            self.arduino.update_lcd_idle()

            # read events from google calendar
            #self.update_events("null")

            self.media.set_stream_url(radio_triplej_url)

            # Testing
            #self.test_radio()
            self.alarm_event(datetime.datetime.now())

        # update time on arduino
        #self.update_lcd_idle("null")

    def update_events(self, event_time):
        print("Updating events")
        self.gcal = GoogleCalendar()
        # get events
        alarm_events = self.gcal.get_alarm_events()

        self.sched.sync_events(alarm_events, self.alarm_event)

        # scedule next event update
        now = datetime.datetime.now()
        next_update_time = datetime.datetime.now() + datetime.timedelta(seconds=self.update_interval)
        print(now.time())
        print(next_update_time.time())
        self.sched.schedule_event(next_update_time, self.update_events)

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
        self.update_lcd_idle("null")

    def alarm_event(self, event_time):
        self.state = "playing"
        self.media.play_stream()
        self.alarm_running = True
        self.update_lcd_playing("null")
        print("woop")
        pass

    def run_alarm_button(self):
        while True:
            if self.alarm_running:
                self.gpio.snooze_button_led_on()
                time.sleep(0.5)
                self.gpio.snooze_button_lef_off()
                time.sleep(0.5)

    def run(self):
        self.webserver.run()
        alarm_btn_thread = threading.Thread(target=self.run_alarm_button())
        alarm_btn_thread.daemon = True
        alarm_btn_thread.start()

if __name__ == "__main__":
    print("Start.")
    clock = NetRadioAlarmClock()
    clock.setup()
    clock.run()
    print("Running")