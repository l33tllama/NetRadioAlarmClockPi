import datetime

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

class GoogleCalendar():

    def __init__(self):

        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
        """Shows basic usage of the Google Calendar API.
        Prints the start and name of the next 10 events on the user's calendar.
        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('../token.pickle'):
            with open('../token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    '/home/pi/Python/NetRadioAlarmClockPi/credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('../token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build('calendar', 'v3', credentials=creds)

    def get_alarm_events(self):
        alarm_events = []

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = self.service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        for event in events:
            if event['summary'] == "Leo's Alarm":
                start = event['start'].get('dateTime', event['start'].get('date'))
                start = start[:22] + start[23:]
                print("Leo's Alarm at: " + start)
                # 2019-03-11T07:00:00+11:00
                date = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                alarm_events.append(date.strftime("%Y-%m-%d %H:%M:%S"))
                print("datetime loaded? " + date.strftime("%Y-%m-%d %H:%M:%S"))

        return alarm_events
        #start = event['start'].get('dateTime', event['start'].get('date'))
        #print(start, event['summary'])
