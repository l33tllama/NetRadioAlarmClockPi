from mpd import MPDClient, ConnectionError
from smbus2 import i2c_msg, SMBus
import RPi.GPIO as GPIO
import time
import threading
import datetime
import pickle
import os.path
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
        #self.client.load("Radio")
    
    def set_volume(self, volume):
        try:
            self.client.setvol(volume)
        except ConnectionError:
            print("Connection to MPD error.")
        
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
        pass
    
    def schedule_event(self, time, event):
        pass

    def cancel_events(self):
        pass

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
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])

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
    
    def set_vol_change_func(self, func):
        self.vol_change_func = func

    def run(self):
        #try:
        while True:
            self.lock.acquire()
            try:
                #self.bus.write_i2c_block_data(self.arduino_addr, 0x00, self.get_vol_arr)
                global i2c_lock
                if not i2c_lock:
                    i2c_lock = True
                    try:
                        self.bus.write_byte(self.arduino_addr, 0x01)
                    except OSError:
                        print("OS Error (write)")
                    finally:
                        i2c_lock = False
                time.sleep(0.1)
                if not i2c_lock:
                    i2c_lock = True
                    try:
                        self.read_volume = self.bus.read_byte_data(self.arduino_addr, 0)
                    except OSError:
                        print("OS error (read)")
                    finally:
                        i2c_lock = False
                else:
                    print("I2C lock receiving volume.")
                #print(self.read_volume)
                if self.read_volume != self.last_read_volume:
                    self.vol_change_func(self.read_volume)
                    print(self.read_volume)
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
        except:
            print("Error starting thread")

    def write_data(self, data):
        byte_value = StringToBytes(data)
        global i2c_lock
        if not i2c_lock:
            i2c_lock = True
            self.bus.write_i2c_block_data(self.address, 0x00, byte_value)
            i2c_lock = False
        else:
            print("Can't write - i2c lock")
        
    
    def update_lcd_playing(self, station_name, artist, title, date_time):
        pass

    def update_lcd_idle(self):
        localtime = time.localtime(time.time())
        print("Local time: " + time.asctime(localtime))
        time_str = str(localtime.tm_wday+1)
        time_str += "-" + str(localtime.tm_mday).zfill(2)
        time_str += "-" + str(localtime.tm_mon).zfill(2)
        time_str += "-" + str(localtime.tm_year)
        time_str += "-" + str(localtime.tm_hour).zfill(2)
        time_str += "-" + str(localtime.tm_min).zfill(2)
        time_str += "-" + str(localtime.tm_sec).zfill(2)
        print("String to send: " + time_str)
        self.write_data("clki:"+time_str)

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
        self.gcal = GoogleCalendar()
        self.arduino = ArduinoController(0x08)
        self.gpio = RPiGPIO()

        self.gpio.reset_arduino()
        
        self.arduino.set_vol_change_callback(self.mpdc.set_volume)
        self.arduino.start_rot_enc_thread()

    def run(self):
        print("Station: " + self.mpdc.get_station_name())
        print("Artist: " + self.mpdc.get_artist())
        print("Title: " + self.mpdc.get_title())

        self.arduino.update_lcd_idle()
        self.gpio.snooze_button_led_on()

        while True:
            self.gpio.snooze_button_led_on()
            time.sleep(0.5)
            self.gpio.snooze_button_lef_off()
            time.sleep(0.5)

if __name__ == "__main__":
    clock = NetRadioAlarmClock()
    clock.run()