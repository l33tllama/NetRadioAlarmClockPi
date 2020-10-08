import time

from smbus2 import SMBus

from global_functions import StringToBytes
from rotary_encoder import RotEncThread

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
        if len(data) > 31:
            print("Data length too long!!")
        data = data[:31]
        print("Writing: " + str(data))
        byte_value = StringToBytes(data)
        global i2c_lock
        # if not i2c_lock:
        # i2c_lock = True
        self.rot_enc_thread.pause()
        print("Writing " + str(byte_value))
        self.bus.write_i2c_block_data(self.address, 0x00, byte_value)
        self.rot_enc_thread.resume()
        # i2c_lock = False
        # else:
        #   print("Can't write - i2c lock")

    def update_lcd_playing(self, station_name, artist, title):
        print("Updating radio data: {stat} {art} {tit}".format(stat=station_name, art=artist, tit=title ) )
        station_name = station_name[:33]
        artist = artist[:33]
        title = title[:33]
        localtime = time.localtime(time.time())
        # print("Local time: " + time.asctime(localtime))
        time_str = str(localtime.tm_wday + 1)
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
        print("Local time: " + time.asctime(localtime))
        time_str = str(localtime.tm_wday + 1)
        time_str += "-" + str(localtime.tm_mday).zfill(2)
        time_str += "-" + str(localtime.tm_mon).zfill(2)
        time_str += "-" + str(localtime.tm_year)
        time_str += "-" + str(localtime.tm_hour).zfill(2)
        time_str += "-" + str(localtime.tm_min).zfill(2)
        time_str += "-" + str(localtime.tm_sec).zfill(2)
        # print("String to send: " + time_str)
        self.write_data("clki:" + time_str)