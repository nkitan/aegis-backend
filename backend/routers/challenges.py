
from fastapi import APIRouter, Depends
from models.challenges import Challenge
from models.user import User
from core.auth import get_current_user
from services.firestore_service import FirestoreService
from typing import List

router = APIRouter()

firestore_service = FirestoreService()

@router.post("/challenges", response_model=Challenge)
def start_challenge(challenge: Challenge, current_user: User = Depends(get_current_user)):
    """
    Starts a new savings challenge for the authenticated user.
    """
    challenge.user_id = current_user.uid
    challenge_id = firestore_service.add_challenge(current_user.uid, challenge.dict())
    challenge.id = challenge_id
    return challenge

@router.get("/challenges", response_model=List[Challenge])
def get_challenges(current_user: User = Depends(get_current_user)):
    """
    Checks the progress of the authenticated user's active challenges.
    """
    return firestore_service.get_challenges(current_user.uid)
