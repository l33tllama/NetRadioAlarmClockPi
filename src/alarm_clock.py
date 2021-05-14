import time
import threading
import datetime

from multimedia_controller import MultimmediaController
from rpi_gpio import RPiGPIO
from scheduler import Scheduler
from text_to_speech import TextToSpeech
import webserver
import sys
from radio_db import RadioDB
from arduino_controller import ArduinoController
from queue import Queue

radio_triplej_url = "http://www.abc.net.au/res/streaming/audio/mp3/triplej.pls"

i2c_lock = False

class NetRadioAlarmClock():
    def __init__(self):
        self.queue = Queue()
        self.alarm_running_queue = Queue()
        self.media = MultimmediaController()
        self.sched = Scheduler()
        self.tts = TextToSpeech()
        self.schedule = {}
        #self.gcal = GoogleCalendar()
        self.arduino = ArduinoController(0x08, self.queue)
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
        self.webserver.alarm_running_queue = self.alarm_running_queue
        self.alarm_running = False
        self.update_interval = 60 * 5
        self.state = "idle"
        self.gpio.set_snooze_btn_callback(self.alarm_snooze_event)
        self.webdev = False
        self.stream_playing = False
        self.alarm_running_queue.put(False)
        self.last_snooze_time = None
        self.button_press_count = 0
        self.debouncing = False

        # Set current station
        url, station_title = self.get_current_station()
        self.media.set_stream_url(url)

        # Load radio alarm schedule and set up events if there are any
        self.load_schedule()
        self.create_events()

        # Test event
        test_time = datetime.datetime(2021, 2, 23, 20, 14, 0)
        self.sched.add_event(test_time, self.alarm_event)

        if len(sys.argv) > 1:
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

    def start_stream(self, queue):
        self.media.play_stream()
        self.stream_playing = True
        queue.put(True)
        volume = self.media.get_volume()
        url, station_name = self.get_current_station()
        if not self.webdev:
            self.update_lcd_playing("null")
        self.webserver.emit_status(self.stream_playing, volume, station_name)


    def stop_stream(self, queue):
        self.media.stop_stream()
        self.stream_playing = False
        queue.put(False)
        volume = self.media.get_volume()
        url, station_name = self.get_current_station()
        webserver.emit_status(self.stream_playing, volume, station_name)

    def setup(self):
        #print("Station: " + self.mpdc.get_station_name())
        #print("Artist: " + self.mpdc.get_artist())
        #print("Title: " + self.mpdc.get_title())

        if not self.webdev:
            #time.sleep(5)
            # display idle screen
            print("Updating arduino idle (with time)")
            self.arduino.update_lcd_idle()

            # read events from google calendar
            #self.update_events("null")
            #self.media.set_stream_url(radio_triplej_url)

            # Testing
            #self.test_radio()
            #self.alarm_event(datetime.datetime.now())
            pass

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
        #print("station: " + station)

        self.arduino.update_lcd_playing(station, "", "")
        #one_second = datetime.datetime.now() + datetime.timedelta(seconds=1)
        #if self.state == "playing":
        #    self.sched.schedule_event(one_second, self.update_lcd_playing)

    
    def update_lcd_idle(self):
        self.arduino.update_lcd_idle()
        #one_second = datetime.datetime.now() + datetime.timedelta(seconds=1)
        
        #if self.state == "idle":
        #    self.sched.schedule_event(one_second, self.update_lcd_idle)
    def alarm_snooze_delay(self):
        # If button pressed only once - snoozing
        if self.button_press_count == 1:
            print("SNOOZING!! ZZZZ")
            now = datetime.datetime.now()
            h = str(now.hour)
            m = str(now.minute)
            if now.minute < 10:
                m = "0" + m
            text = "Snoozing. The time is now {hr} {min}".format(hr=h, min=m)
            self.tts.say(text)
            self.state = "snooze"
            self.media.stop_stream()
            self.alarm_running = False
            radio_rest_time = datetime.datetime.now() + datetime.timedelta(minutes=7)
            self.sched.add_event(radio_rest_time, self.alarm_event)
            self.alarm_running_queue.put(False)
            self.last_snooze_time = None
            self.button_press_count = 0
            if not self.webdev:
                self.update_lcd_idle()
        elif self.button_press_count > 1:
            print("Alarm OFF! Time to get up!!")
            self.tts.say("Alarm is now off. Time to get up!")
            self.alarm_running_queue.put(False)
            self.media.stop_stream()
            # Clear snooze event
            self.sched.remove_fixed_events()
            self.button_press_count = 0
        else:
            print("Button pressed more than once! I see that.. Alarm stop?")

    def debounce(self):
        self.debouncing = False
        print("Debounced?")

    def alarm_snooze_event(self, channel):
        if not self.debouncing:
            self.button_press_count += 1
            print("Btn count: " + str(self.button_press_count))
            if self.button_press_count == 1:
                self.last_snooze_time = datetime.datetime.now()
                # Check in three seconds if the button has been pressed more than once
                threading.Timer(3, self.alarm_snooze_delay).start()

            self.debouncing = True
            threading.Timer(0.2, self.debounce).start()
        else:
            print("Bounce!")

    def alarm_event(self):
        if self.state == "snooze":
            now = datetime.datetime.now()
            now_h = now.hour
            now_m = now.minute
            if self.last_snooze_time is not None:
                last_m = self.last_snooze_time.minute
                last_h = self.last_snooze_time.hour
                # If we snoozed in the same minute, don't alarm again (bit of a hack)
                if now_h == last_h and now_m == last_m:
                    return
        self.state = "playing"
        self.media.play_stream()
        self.alarm_running = True
        self.alarm_running_queue.put(True)
        if not self.webdev:
            self.update_lcd_playing("null")

    def run_alarm_button(self, queue):
        running = False
        while True:
            data = None
            if not queue.empty():
                data = queue.get()
            if data is True:
                running = True
            elif data is False:
                running = False
            self.sched.process_events()
            time.sleep(1)
            if running:
                #print("Running!")
                self.update_lcd_playing("null")
                self.gpio.snooze_button_led_on()
                time.sleep(0.5)
                self.gpio.snooze_button_lef_off()
                time.sleep(0.5)
            else:
                #print("idle")
                self.arduino.update_lcd_idle()
                time.sleep(4)

    def update_idle_thread(self, queue):
        #self.arduino = ArduinoController(0x08)
        idle = True
        while True:
            data = None
            if not queue.empty():
                data = queue.get()
            if data is False:
                idle = True
            elif data is True:
                idle = False
            if idle:
                #TODO: run main playing screen when playing
                print("Idling")
                self.arduino.update_lcd_idle()
                time.sleep(5)

    def run(self):
        alarm_btn_thread = threading.Thread(target=self.run_alarm_button, args=(self.alarm_running_queue,))
        alarm_btn_thread.daemon = True
        alarm_btn_thread.start()
        #update_idle_thread = threading.Thread(target=self.update_idle_thread, args=(self.alarm_running_queue,))
        #update_idle_thread.daemon = True
        #update_idle_thread.start()
        #while True:
        #    time.sleep(1)
        print("Start web server?")
        self.webserver.run()

if __name__ == "__main__":
    print("Start.")
    clock = NetRadioAlarmClock()
    clock.setup()
    clock.run()
    print("Running")