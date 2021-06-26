import subprocess
import urllib

class MultimmediaController():
    def __init__(self, ):
        self.stream_url = ""
        self.player_process = None
        self.playing = False
        self.volume = 0
        self.current_station_title = ""

    def set_stream_url(self, stream_url):
        self.stream_url = self.get_url_from_playlist_file(stream_url)

    @staticmethod
    def get_radio_url_from_pls(playlist_file_url):
        contents = str(urllib.request.urlopen(playlist_file_url).read())
        file1_pos = contents.find("File1")
        after_file_1 = contents[file1_pos + 6:]
        new_line_pos = after_file_1.find('\\r')
        radio_url = after_file_1[:new_line_pos - 1]
        return radio_url

    @staticmethod
    def get_radio_url_from_m3u(playlist_file_url):
        contents = str(urllib.request.urlopen(playlist_file_url).read())
        http_pos = contents.find("http:")
        after_http = contents[http_pos:]
        new_line_pos = after_http.find('\\r')
        radio_url = after_http[:new_line_pos - 1]
        return radio_url

    def get_url_from_playlist_file(self, url) -> str:
        stream_url = ""
        if ".m3u" in url or ".m3u8" in url:
            print("M3U file detected.")
            stream_url = self.get_radio_url_from_m3u(url)
        elif ".pls" in url:
            print("PLS file detected.")
            stream_url = self.get_radio_url_from_pls(url)
        else:
            stream_url = url

        return stream_url

    def get_title_from_any_url(self, url):
        stream_url = ""
        if ".m3u" in url or ".m3u8" in url:
            print("M3U file detected.")
            stream_url = self.get_radio_url_from_m3u(url)
        elif ".pls" in url:
            print("PLS file detected.")
            stream_url = self.get_radio_url_from_pls(url)
        else:
            stream_url = url

        title = self.get_station_title(station_url=stream_url)
        return title

    def get_station_title(self, station_url=""):
        header = {'Icy-MetaData': 1}
        request = None
        response = None
        if station_url != "":
            request = urllib.request.Request(station_url, headers=header)
        else:
            station_url = self.stream_url
            request = urllib.request.Request(station_url, headers=header)
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.URLError as e:
            print(e)
            # Try again..
            return "URLError"
        except TimeOutError as e:
            print(e)
            return "Timeout"
        icy_metaint_header = response.headers.get('icy-metaint')
        if icy_metaint_header is not None:
            metaint = int(icy_metaint_header)
            read_buffer = metaint + 255
            try:
                content = response.read(read_buffer)
            except ConnectionResetError as e:
                print(e)
            content_str = ""
            for _byte in content:
                content_str += chr(int(_byte))

            stream_title_pos = content_str.find("StreamTitle=")
            station_name = ""
            if stream_title_pos > 0:
                post_title_content = content_str[stream_title_pos + 13:]
                semicolon_pos = post_title_content.find(';')
                station_name = post_title_content[:semicolon_pos - 1]
            else:
                station_name = station_url[7:39]
            self.current_station_title = station_name
            return station_name
        else:
            return "No data"

    def play_stream(self):
        if self.playing:
            self.stop_stream()
            self.play_stream()
        else:
            self.player_process = subprocess.Popen(["/usr/bin/mpg123", "-@" + self.stream_url])
            self.playing = True

    def get_playing(self):
        return self.playing

    def stop_stream(self):
        if self.player_process:
            self.player_process.kill()
        self.playing = False

    def set_volume(self, volume):
        print("Setting volume: " + str(volume))
        self.volume = volume
        volume_scaled = (volume / 100) * 65536
        subprocess.call(["/usr/bin/amixer", "sset", "'Master'", str(volume_scaled)])

    def get_volume(self):
        return self.volume