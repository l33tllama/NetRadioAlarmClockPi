import threading
import time
from queue import Queue

from smbus2 import SMBus

class RotEncThread(threading.Thread):
    def __init__(self, i2c_address, queue):
        threading.Thread.__init__(self)
        self.read_volume = 0
        self.last_read_volume = 0
        self.vol_change_func = None
        self.arduino_addr = i2c_address
        self.bus = SMBus(1)
        self.get_vol_arr = [103, 101, 116, 118, 0]
        #self.lock = threading.Lock()
        self.paused = False
        self.queue = queue

    def set_vol_change_func(self, func):
        self.vol_change_func = func

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def run(self):
        # try:
        while True:
            data = None
            if not self.queue.empty():
                data = self.queue.get()
            if data is not None:
                if data is False:
                    #print("ROT ENC THREAD PAUSING")
                    self.paused = True
                else:
                    #print("ROT ENC THREAD RESUMING")
                    self.paused = False
            else:
                self.paused = True
            try:
                if not self.paused:
                    try:
                        self.bus.write_i2c_block_data(self.arduino_addr, 0x00, self.get_vol_arr)
                    except IOError as e:
                        print(e)
                    except OSError as e:
                        print(e)
                global i2c_lock
                if not self.paused:
                    # i2c_lock = True
                    try:
                        self.bus.write_byte(self.arduino_addr, 0x01)
                        pass
                    except OSError:
                        print("OS Error (write)")
                        pass
                    finally:
                        pass
                        # i2c_lock = False
                #time.sleep(0.1)
                if not self.paused:
                    # i2c_lock = True
                    try:
                        self.read_volume = self.bus.read_byte_data(self.arduino_addr, 0)
                        pass
                    except OSError:
                        pass
                        print("OS error (read)")
                    finally:
                        pass
                        # i2c_lock = False
                else:
                    pass
                    # print("I2C lock receiving volume.")
                #print(self.read_volume)
                if not self.paused:
                    random_zero = False
                    if self.read_volume != self.last_read_volume:

                        if self.read_volume == 0:
                            random_zero = True
                        else:
                            self.vol_change_func(self.read_volume)
                            #print("vol: " + str(self.read_volume))
                    if random_zero:
                        pass
                    else:
                        self.last_read_volume = self.read_volume
            finally:
                #self.lock.release()
                pass
                #time.sleep(0.01)
    # finally:
    #    GPIO.cleanup()