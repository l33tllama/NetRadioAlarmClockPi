# NetRadioAlarmClockPi

## Main Python program that runs my Internet Radio Alarm clock.

What is my Internet Radio Alarm clock?

It's a home-made alarm clock that plays Internet radio streams to wake you up in the morning.
The components consist of
* Raspberry PI Zero W
* Arduino Nano
* 128x64 graphical B&W LCD
* Phat DAC for audio output
* DS1307 RTC module - connected to Pi over I2C bus
* Stereo speakers and amp module
* Big snooze pushbutton
* Rotary encoder for volume
* 3D printed chassis - see [https://github.com/l33tllama/NetRadioAlarmClockCase](https://github.com/l33tllama/NetRadioAlarmClockCase)

The main Python program consists of several files and classes containing the functionality.

In code, it uses:
* A SQLite database for storing alarms and radio stations.
* `smbus2` for I2C communications. A very good way to communicate to Arduino via Python. You just need a logic voltage level shifter.
* The Linux command-line program `mpg123` to stream radio station URLs.
* My own scheduler class that calls functions at certain times. Very basic but it works.
* The Python library [https://github.com/asrp/python-espeak](https://github.com/asrp/python-espeak) for text to speech for alerting some events.
* Flask and Flask SocketIO for the webserver and websocket connection for realtime control.
