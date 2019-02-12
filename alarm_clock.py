from mpd import MPDClient

class MPDController():
    def __init__(self):
        self.client = MPDClient()
        self.client.timeout = 10
        self.client.idletimeout = None
        self.client.connect("localhost", 6600)
        self.client.load("Radio")
    
    def set_volume(self, volume):
        self.client.setvol(volume)
        
    def play(self):
        self.client.play()

    def stop(self):
        self.client.stop()

    def get_station_name(self):
        current_song = self.client.currentsong()
        return current_song['name']

    def get_artist(self):
        try:
            current_song = self.client.currentsong()
            return current_song['artist']
        except KeyError:
            return ""

    def get_title(self):
        current_song = self.client.currentsong()
        return current_song['title']

class Scheduler():
    def __init__(self):
        pass
    
    def schedule_event(self, time, event):
        pass

    def cancel_events(self):
        pass

class GoogleCalendar():

    def __init__(self):
        pass

    def get_alarm_events(self):
        pass

class ArduinoController():

    def __init__(self, i2c_address):
        pass
    
    def update_lcd_playing(self, station_name, artist, title, date_time):
        pass

    def update_lcd_idle(self, date_time):
        pass
    
    def get_volume(self):
        pass

class NetRadioAlarmClock():

    def __init__(self):
        self.mpdc = MPDController()
        self.sched = Scheduler()
        self.gcal = GoogleCalendar()
        self.arduino = ArduinoController(0x08)

    def run(self):
        print("Station: " + self.mpdc.get_station_name())
        print("Artist: " + self.mpdc.get_artist())
        print("Title: " + self.mpdc.get_title())

if __name__ == "__main__":
    clock = NetRadioAlarmClock()
    clock.run()