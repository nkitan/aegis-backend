
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    uid: str
    email: EmailStr
    display_name: str | None = None
    fcm_token: str | None = None
    id_token: str | None = None
