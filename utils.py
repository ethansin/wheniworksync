import datetime
import os.path
import os
import requests

from icalendar import Calendar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build 

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def parse_event_datetime(event_dt: dict) -> str:
    if "dateTime" in event_dt:
        dt = datetime.datetime.fromisoformat(event_dt["dateTime"].replace("Z", "+00:00"))
    else:
        # All-day event (just 'YYYY-MM-DD'), treat as midnight UTC
        dt = datetime.datetime.fromisoformat(event_dt["date"] + "T00:00:00+00:00")

    dt = dt.astimezone(datetime.timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")

def load_calendar_events(filepath: str) -> list[dict]:
    events = []
    with open(filepath, 'rb') as cal_file:
        gcal = Calendar.from_ical(cal_file.read())
    for component in gcal.walk():
        if component.name == "VEVENT":
            event = {}
            event['summary'] = component.get('summary', 'untitled')
            event['start'] = component.get('dtstart').dt.isoformat().replace("+00:00", "Z")
            event['end'] = component.get('dtend').dt.isoformat().replace("+00:00", "Z")
            events.append(event)
    return events

def get_calendar_service():
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
    return build("calendar", "v3", credentials=creds)

def event_exists(service, calendar_id, event):
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=event["start"],
        timeMax=event["end"],
        q=event["summary"],
        singleEvents=True
    ).execute()
    
    for existing in events_result.get("items", []):
        if (existing["summary"] == event["summary"] and
            parse_event_datetime(existing["start"]) == event["start"] and
            parse_event_datetime(existing["end"]) == event["end"]):
            return True
    return False

def create_events(events, calendar_id="primary"):
    service = get_calendar_service()

    for event in events:
        event_body = {
            "summary": event["summary"],
            "start": {"dateTime": event["start"], "timeZone": "UTC"},
            "end": {"dateTime": event["end"], "timeZone": "UTC"},
        }

        if not event_exists(service, calendar_id, event):
            created_event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
            print(f'Created: {created_event.get("htmlLink")}')
        else:
            print(f'Skipped duplicate: {event["summary"]} ({event["start"]})')

def download_file(url):
    filename = url.split("/")[-1]
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    
    print(f"Downloaded: {filepath}")
    return filepath