import datetime
import pytz
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import tkinter as tk

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + "Z"
    print("Getting the upcoming 10 events")
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])

    if not events:
        print('No upcoming events found.')
        return []

    event_list = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        
        if 'dateTime' in event['start']:
            start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
            end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
            jst = pytz.timezone('Asia/Tokyo')
            start_jst = start_dt.astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
            end_jst = end_dt.astimezone(jst).strftime('%Y-%m-%d %H:%M:%S')
        else:
            start_jst = start
            end_jst = end
        
        event_list.append(f"開始時間: {start_jst}, 終了時間: {end_jst}, タスク: {event['summary']}")
    
    return event_list

def display_events(events):
    root = tk.Tk()
    root.title("Upcoming Events")
    for event in events:
        label = tk.Label(root, text=event)
        label.pack()
    root.mainloop()

if __name__ == '__main__':
    events = main()
    if events:
        display_events(events)