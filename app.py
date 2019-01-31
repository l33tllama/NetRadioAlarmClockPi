#!/usr/bin/python

#import smbus
from smbus2 import i2c_msg, SMBus
import time
from mpd import MPDClient
from RPi import GPIO
import threading

PIN_CLK = 22
PIN_DT = 23

address = 0x08
bus = SMBus(1)
client = None

counter = 0
lock = threading.Lock()
clk_last_state = 0

class RotEncThread(threading.Thread):
    global clk_last_state

    def __init__(self):
        threading.Thread.__init__(self)
        self.clkState = 0
        self.dtState = 0
        self.clk_last_state = 0
        self.counter = 0
        self.volume = 100
        self.vol_change_func = None
    
    def set_vol_change_func(self, func):
        self.vol_change_func = func

    def run(self):
        try:
            while True:
                lock.acquire()
                try:
                    self.clkState = GPIO.input(PIN_CLK)
                    self.dtState = GPIO.input(PIN_DT)
                    if self.clkState != self.clk_last_state:
                        if self.dtState != self.clkState:
                            if self.counter < self.volume:
                                self.counter += 1
                        else:
                            if self.counter > 0:
                                self.counter -= 1 
                        self.vol_change_func(self.counter) 
                        print(str(self.counter))
                    self.clk_last_state = self.clkState
                finally:
                    lock.release()
                    time.sleep(0.001)
        finally:
            GPIO.cleanup()

def setup_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN_CLK, GPIO.IN,  pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(PIN_DT, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def write_number(value):
	bus.write_byte(address, value)
	return -1

def start_rot_enc_thread():
    clk_last_state = GPIO.input(PIN_CLK)
    rot_enc_thread = None
    try:
       rot_enc_thread = RotEncThread()
       rot_enc_thread.set_vol_change_func(send_volume)
       rot_enc_thread.daemon = True
       rot_enc_thread.start()
    except:
        print("Error starting thread")

def write_data(data):
	byte_value = StringToBytes(data)
	bus.write_i2c_block_data(address, 0x00, byte_value)
	return -1

def read_data(length):
    data = []
    for i in range(length):
        data.append(bus.read_byte_data(80, 0))
    #block = bus.read_i2c_block_data(address, 0x00, length)
    print(str(data))
    return data

def StringToBytes(val):
    ret_val = []
    for c in val:
        ret_val.append(ord(c))
        #print(c)

    ret_val.append(0)
    return ret_val

def BytesToString(bytes_arr):
    str_out = ""
    for b in bytes_arr:
        str_out += chr(b)
    return str_out

def read_write(command, length):
    cmd_bytes = StringToBytes(command)
    write = i2c_msg.write(80, cmd_bytes)
    read = i2c_msg.read(80, length)
    bus.i2c_rdwr(write, read)
    for i in range(read.len):
        print(read.buf[i])

def get_volume():
    #write_data("getv:abc")
    #volume = read_data(4)
    read_write("getv", 4)
    #return volume

#write_data("Python FTW ")

def send_volume(volume):
    send_str = "volc:" + str(volume).zfill(2)
    write_data(send_str)
    print("Sending volume: " + send_str )

def connect_to_mpd():
    client = MPDClient()
    client.timeout = 10
    client.idletimeout = None
    client.connect("localhost", 6600)

def send_current_song():
    current_song = client.currentsong()
    song_title = current_song["title"]
    print("Current song " + str(current_song))
    write_data(song_title)

def send_time_idle():
    localtime = time.localtime(time.time())
    print("Local time: " + time.asctime(localtime))
    time_str = str(localtime.tm_wday+1)
    time_str += "-" + str(localtime.tm_mday)
    time_str += "-" + str(localtime.tm_mon).zfill(2)
    time_str += "-" + str(localtime.tm_year)
    time_str += "-" + str(localtime.tm_hour).zfill(2)
    time_str += "-" + str(localtime.tm_min).zfill(2)
    time_str += "-" + str(localtime.tm_sec).zfill(2)
    print("String to send: " + time_str)
    write_data("clki:"+time_str)

setup_gpio()
#start_rot_enc_thread()
send_time_idle()
time.sleep(0.5)
#send_time_idle()
#vol = get_volume()
test = bus.read_i2c_block_data(address, 0, 4)
#test = BytesToString(read_data(20))
print(test)

#bytess = StringToBytes("Hello")
#print(bytess)

#while True:
    #time.sleep(1)
