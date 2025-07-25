
from googleapiclient.discovery import build
from google.oauth2 import service_account
from core.config import settings

class GoogleCalendarService:
    def __init__(self):
        creds = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_CALENDAR_SERVICE_ACCOUNT_KEY_FILE,
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        self.service = build('calendar', 'v3', credentials=creds)

    def create_event(self, event_data: dict) -> str:
        """
        Creates a Google Calendar event and returns the event ID.
        """
        event = self.service.events().insert(calendarId='primary', body=event_data).execute()
        return event.get('id')
