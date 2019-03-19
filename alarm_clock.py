from mpd import MPDClient, ConnectionError, ProtocolError
from smbus2 import i2c_msg, SMBus
import RPi.GPIO as GPIO
import time
import threading
import datetime
import pickle
import os.path
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def StringToBytes(val):
    ret_val = []
    for c in val:
        ret_val.append(ord(c))
        #print(c)

    ret_val.append(0)
    return ret_val

class MPDController():
    def __init__(self):
        self.client = MPDClient()
        self.client.timeout = 10
        self.client.idletimeout = None
        self.client.connect("localhost", 6600)
        self.client.load("Radio")
    
    def set_volume(self, volume):
        try:
            self.client.setvol(volume)
        except ConnectionError:
            print("Connection to MPD error.")
        except ProtocolError:
            print("Got garbage data")
        
    def play(self):
        self.client.play()

    def stop(self):
        self.client.stop()

    def get_station_name(self):
        current_song = self.client.currentsong()
        try:
            return current_song['name']
        except KeyError:
            return ""

    def get_artist(self):
        try:
            current_song = self.client.currentsong()
            return current_song['artist']
        except KeyError:
            return ""

    def get_title(self):
        current_song = self.client.currentsong()
        try:
            return current_song['title']
        except KeyError:
            return ""

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
                #Schedule event
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

class GoogleCalendar():
    

    def __init__(self):

        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_alarm_events(self):
        alarm_events = []

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            if event['summary'] == "Leo's Alarm":   
                start = event['start'].get('dateTime', event['start'].get('date'))
                start = start[:22] + start[23:]
                print("Leo's Alarm at: " + start)
                # 2019-03-11T07:00:00+11:00
                date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                alarm_events.append(date.strftime("%Y-%m-%d %H:%M:%S"))
                print("datetime loaded? " + date.strftime("%Y-%m-%d %H:%M:%S"))

        return alarm_events
        #start = event['start'].get('dateTime', event['start'].get('date'))
        #print(start, event['summary'])

i2c_lock = False

class RotEncThread(threading.Thread):

    def __init__(self, i2c_address):
        threading.Thread.__init__(self)
        self.read_volume = 0
        self.last_read_volume = 0
        self.vol_change_func = None
        self.arduino_addr = i2c_address
        self.bus = SMBus(1)
        self.get_vol_arr = [103, 101, 116, 118, 0]
        self.lock = threading.Lock()
        self.paused = False
    
    def set_vol_change_func(self, func):
        self.vol_change_func = func

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def run(self):
        #try:
        while True:
            self.lock.acquire()
            try:
                #self.bus.write_i2c_block_data(self.arduino_addr, 0x00, self.get_vol_arr)
                global i2c_lock
                if not self.paused:
                    #i2c_lock = True
                    try:
                       self.bus.write_byte(self.arduino_addr, 0x01)
                       pass
                    except OSError:
                        #print("OS Error (write)")
                        pass
                    finally:
                        pass
                        #i2c_lock = False
                time.sleep(0.1)
                if not self.paused:
                    #i2c_lock = True
                    try:
                        self.read_volume = self.bus.read_byte_data(self.arduino_addr, 0)
                        pass
                    except OSError:
                        pass
                        #print("OS error (read)")
                    finally:
                        pass
                        #i2c_lock = False
                else:
                    pass
                    #print("I2C lock receiving volume.")
                #print(self.read_volume)
                if not self.paused:
                    random_zero = False
                    if self.read_volume != self.last_read_volume:
                        
                        if self.read_volume == 0:
                            random_zero = True
                        else:
                            self.vol_change_func(self.read_volume)
                            print("vol: " + str(self.read_volume))
                    if random_zero:
                        pass
                    else:
                        self.last_read_volume = self.read_volume
            finally:
                self.lock.release()
                time.sleep(0.01)
       #finally:
        #    GPIO.cleanup()

class ArduinoController():

    def __init__(self, i2c_address):
        self.bus = SMBus(1)
        self.address = i2c_address
        self.rot_enc_thread = None
        self.vol_change_cb = None
    
    def set_vol_change_callback(self, vol_change_cb):
        self.vol_change_cb = vol_change_cb

    def start_rot_enc_thread(self):
        try:
            self.rot_enc_thread = RotEncThread(self.address)
            self.rot_enc_thread.set_vol_change_func(self.vol_change_cb)
            self.rot_enc_thread.daemon = True
            self.rot_enc_thread.start()
            pass
        except:
            print("Error starting thread")

    def write_data(self, data):
        byte_value = StringToBytes(data)
        global i2c_lock
        #if not i2c_lock:
            #i2c_lock = True
        self.rot_enc_thread.pause()
        self.bus.write_i2c_block_data(self.address, 0x00, byte_value)
        self.rot_enc_thread.resume()
            #i2c_lock = False
        #else:
        #   print("Can't write - i2c lock")
        
    
    def update_lcd_playing(self, station_name, artist, title):
        station_name = station_name[:33]
        artist = artist[:33]
        title = title[:33]
        localtime = time.localtime(time.time())
        #print("Local time: " + time.asctime(localtime))
        time_str = str(localtime.tm_wday+1)
        time_str += "-" + str(localtime.tm_mday).zfill(2)
        time_str += "-" + str(localtime.tm_mon).zfill(2)
        time_str += "-" + str(localtime.tm_year)
        time_str += "-" + str(localtime.tm_hour).zfill(2)
        time_str += "-" + str(localtime.tm_min).zfill(2)
        time_str += "-" + str(localtime.tm_sec).zfill(2)
        self.write_data("stat:" + station_name)
        time.sleep(0.1)
        self.write_data("arti:" + artist)
        time.sleep(0.1)
        self.write_data("titl:" + title)
        time.sleep(0.1)
        self.write_data("clkp:" + time_str)

    def update_lcd_idle(self):
        localtime = time.localtime(time.time())
        #print("Local time: " + time.asctime(localtime))
        time_str = str(localtime.tm_wday+1)
        time_str += "-" + str(localtime.tm_mday).zfill(2)
        time_str += "-" + str(localtime.tm_mon).zfill(2)
        time_str += "-" + str(localtime.tm_year)
        time_str += "-" + str(localtime.tm_hour).zfill(2)
        time_str += "-" + str(localtime.tm_min).zfill(2)
        time_str += "-" + str(localtime.tm_sec).zfill(2)
        #print("String to send: " + time_str)
        self.write_data("clki:" + time_str)
        

class RPiGPIO():

    def __init__(self):
        self.reset_pin = 17
        self.snooze_btn_pin = 27
        self.snooze_btn_led_pin = 22
        GPIO.setmode(GPIO.BCM)
        # Reset line
        GPIO.setup(self.reset_pin, GPIO.OUT)
        # snooze button
        GPIO.setup(self.snooze_btn_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        # snooze button LED
        GPIO.setup(self.snooze_btn_led_pin, GPIO.OUT)
        GPIO.output(self.reset_pin, GPIO.HIGH)
    
    def snooze_button_led_on(self):
        GPIO.output(self.snooze_btn_led_pin, GPIO.HIGH)

    def snooze_button_lef_off(self):
        GPIO.output(self.snooze_btn_led_pin, GPIO.LOW)
    
    def reset_arduino(self):
        GPIO.output(self.reset_pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.reset_pin, GPIO.HIGH)
        time.sleep(3.5)

class NetRadioAlarmClock():

    def __init__(self):
        self.mpdc = MPDController()
        self.sched = Scheduler()
        #self.gcal = GoogleCalendar()
        self.arduino = ArduinoController(0x08)
        self.gpio = RPiGPIO()
        self.alarm_running = True
        self.update_interval = 60 * 5
        self.state = "idle"

        print("Resetting Arduino")
        self.gpio.reset_arduino()
        print("Done")
        
        self.arduino.set_vol_change_callback(self.mpdc.set_volume)
        self.arduino.start_rot_enc_thread()

    
    def setup(self):
        print("Station: " + self.mpdc.get_station_name())
        print("Artist: " + self.mpdc.get_artist())
        print("Title: " + self.mpdc.get_title())

        # display idle screen
        self.arduino.update_lcd_idle()

        # read events from google calendar
        #self.update_events("null")

        # Testing
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

        station = self.mpdc.get_station_name()
        artist = self.mpdc.get_artist()
        title = self.mpdc.get_title()

        self.arduino.update_lcd_playing(station, artist, title)

        one_second = datetime.datetime.now() + datetime.timedelta(seconds=1)
        
        if self.state == "playing":
            self.sched.schedule_event(one_second, self.update_lcd_playing)

    
    def update_lcd_idle(self, time_str):
        self.arduino.update_lcd_idle()
        one_second = datetime.datetime.now() + datetime.timedelta(seconds=1)
        
        if self.state == "idle":
            self.sched.schedule_event(one_second, self.update_lcd_idle)

    def alarm_event(self, event_time):
        self.state = "playing"
        self.mpdc.play()
        self.update_lcd_playing("null")
        print("woop")
        pass

    def run(self):
        while True:
            if self.alarm_running:
                self.gpio.snooze_button_led_on()
                time.sleep(0.5)
                self.gpio.snooze_button_lef_off()
                time.sleep(0.5)
            # If alarm clock starts playing
            #if self.state == "idle" and self.mpdc.

if __name__ == "__main__":
    print("Start.")
    clock = NetRadioAlarmClock()
    clock.setup()
    clock.run()
    print("Running")