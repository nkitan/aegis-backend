
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from models.user import User
from core.auth import get_current_user
from services.firestore_service import FirestoreService

router = APIRouter()
firestore_service = FirestoreService()

class FCMTokenUpdate(BaseModel):
    fcm_token: str

@router.get("/users/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retrieves the profile of the currently authenticated user.
    """
    return current_user

@router.post("/users/me/fcm_token")
def update_fcm_token(fcm_token_update: FCMTokenUpdate, current_user: User = Depends(get_current_user)):
    """
    Updates the FCM token for the currently authenticated user.
    """
    firestore_service.update_user_fcm_token(current_user.uid, fcm_token_update.fcm_token)
    return {"message": "FCM token updated successfully"}
