from mpd import MPDClient, ConnectionError, ProtocolError

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