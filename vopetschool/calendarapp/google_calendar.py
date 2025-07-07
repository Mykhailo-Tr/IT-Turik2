import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_google_credentials(user_id):
    token_path = os.path.join(settings.BASE_DIR, 'tokens', f'{user_id}_token.json')
    if os.path.exists(token_path):
        return Credentials.from_authorized_user_file(token_path, SCOPES)
    return None

def create_google_event(user_id, title, description, start_dt, end_dt):
    creds = get_google_credentials(user_id)
    if not creds:
        return False
    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': title,
        'description': description,
        'start': {'dateTime': start_dt.isoformat(), 'timeZone': 'Europe/Kyiv'},
        'end': {'dateTime': end_dt.isoformat(), 'timeZone': 'Europe/Kyiv'},
    }
    service.events().insert(calendarId='primary', body=event).execute()
    return True
