from smbus2 import i2c_msg, SMBus
import time
import threading

bus = SMBus(1)
address = 0x08

def StringToBytes(val):
    ret_val = []
    for c in val:
        ret_val.append(ord(c))
        #print(c)

    ret_val.append(0)
    return ret_val

def write_data(data):
    byte_value = StringToBytes(data)
    bus.write_i2c_block_data(address, 0x00, byte_value)

def update_lcd_idle():
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
    write_data("clki:"+time_str)

def update_loop():
    while True:
        update_lcd_idle()
        time.sleep(1)


update_thread = threading.Thread(target=update_loop)
update_thread.daemon = True
update_thread.start()

while True:
    time.sleep(1)