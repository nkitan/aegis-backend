
from fastapi import APIRouter, Depends
from models.integrations import WalletPassRequest, CalendarEventRequest, NotificationRequest
from models.user import User
from core.auth import get_current_user
from services.google_wallet_service import GoogleWalletService
from services.google_calendar_service import GoogleCalendarService
from services.firebase_notification_service import FirebaseNotificationService

router = APIRouter()

google_wallet_service = GoogleWalletService()
google_calendar_service = GoogleCalendarService()
firebase_notification_service = FirebaseNotificationService()

@router.post("/integrations/wallet/pass")
def create_wallet_pass(request: WalletPassRequest, current_user: User = Depends(get_current_user)):
    """
    Creates a Google Wallet pass.
    """
    pass_url = google_wallet_service.create_pass(request.pass_type, request.pass_data)
    return {"status": "success", "pass_url": pass_url}

@router.post("/integrations/calendar/event")
def create_calendar_event(request: CalendarEventRequest, current_user: User = Depends(get_current_user)):
    """
    Creates a Google Calendar event for warranty or return reminders.
    """
    event_id = google_calendar_service.create_event(request.event_data)
    return {"status": "success", "event_id": event_id}

@router.post("/integrations/notifications/send")
def send_notification(request: NotificationRequest, current_user: User = Depends(get_current_user)):
    """
    Sends a push notification to a user's device via a service like Firebase Cloud Messaging (FCM).
    """
    firebase_notification_service.send_notification(request.user_id, request.message)
    return {"status": "success"}
