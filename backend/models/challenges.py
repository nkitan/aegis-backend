
from pydantic import BaseModel
from typing import Dict

class Challenge(BaseModel):
    id: str | None = None
    user_id: str
    challenge_type: str
    details: Dict
    status: str = "active"
