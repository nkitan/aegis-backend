
from pydantic import BaseModel
from typing import Dict

class WalletPassRequest(BaseModel):
    pass_type: str
    pass_data: Dict

class CalendarEventRequest(BaseModel):
    event_data: Dict

class NotificationRequest(BaseModel):
    user_id: str
    message: str
