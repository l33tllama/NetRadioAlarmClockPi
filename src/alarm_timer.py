import datetime

day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday". "sunday"]

class AlarmTimer():

    def __init__(self):
        self.cb_event = None
        self.enabled_weekdays = []
        self.enabled_weekends = []
        self.weekday_time = ""
        self.weekend_time = ""
        self.alarm_flag = False
        pass

    def add_alarms(self, schedule, cb_event):
        self.enabled_weekdays = schedule["enabled_weekdays"]
        self.enabled_weekends = schedule["enabled_weekend_days"]
        self.weekday_time = schedule["weekday_time"]
        self.weekend_time = schedule["weekend_time"]

    def check_time(self, is_weekend):
        now = datetime.datetime.now()
        hour = now.hour
        min = now.min
        if is_weekend:
            weekend_hour = int(self.weekend_time.split(":")[0])
            weekend_min = int(self.weekend_time.split(":")[1])
            if weekend_hour == hour and weekend_min == min:
                return True
        else:
            weekday_hour = int(self.weekday_time.split(":")[0])
            weekday_min = int(self.weekday_time.split(":")[1])
            if weekday_hour == hour and weekday_min == min:
                return True
        return False

    def process_alarms(self):
        current_day = day_names[datetime.datetime.now().weekday()]
        is_alarm_on = False
        for day in self.enabled_weekends:
            if day == current_day:
                if day == "saturday" or day == "sunday":
                    is_alarm_on = self.check_time(True)
                else:
                    is_alarm_on = self.check_time(False)

        if is_alarm_on and not self.alarm_flag:
            self.alarm_flag = True
            self.cb_event()
        elif not is_alarm_on:
            self.alarm_flag = False