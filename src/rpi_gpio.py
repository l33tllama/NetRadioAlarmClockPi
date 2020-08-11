import time

import RPi.GPIO as GPIO

class RPiGPIO():
    def __init__(self):
        self.reset_pin = 17
        self.snooze_btn_pin = 27
        self.snooze_btn_led_pin = 22
        self.snooze_callback = None
        GPIO.setmode(GPIO.BCM)
        # Reset line
        GPIO.setup(self.reset_pin, GPIO.OUT)
        # snooze button
        GPIO.setup(self.snooze_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # snooze button LED
        GPIO.setup(self.snooze_btn_led_pin, GPIO.OUT)
        GPIO.output(self.reset_pin, GPIO.HIGH)
        # GPIO.add_event_detect(self.snooze_btn_pin, GPIO.FALLING, callback=self.snooze_callback)

    def snooze_button_led_on(self):
        GPIO.output(self.snooze_btn_led_pin, GPIO.HIGH)

    def snooze_button_lef_off(self):
        GPIO.output(self.snooze_btn_led_pin, GPIO.LOW)

    def reset_arduino(self):
        GPIO.output(self.reset_pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.reset_pin, GPIO.HIGH)
        time.sleep(3.5)

    def set_snooze_btn_callback(self, callback):
        # self.snooze_callback = callback
        GPIO.add_event_detect(self.snooze_btn_pin, GPIO.FALLING, callback=callback)