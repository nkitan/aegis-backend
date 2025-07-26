
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import httpx
import logging
from models.user import User
from core.auth import get_current_user
from services.firestore_service import FirestoreService
from services.aegnt_service import AegntService

logger = logging.getLogger(__name__)

router = APIRouter()
firestore_service = FirestoreService()
aegnt_service = AegntService()

class AegntPrompt(BaseModel):
    prompt: str

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

@router.post("/users/me/agent/invoke")
async def invoke_agent_endpoint(prompt: AegntPrompt, current_user: User = Depends(get_current_user)):
    """
    Invokes the Aegnt agent with a prompt from the user.
    """
    try:
        logger.info(f"Invoking agent for user {current_user.uid} with prompt: {prompt.prompt}")
        response = await aegnt_service.invoke_agent(current_user.uid, prompt.prompt)
        logger.info("Successfully received response from agent")
        return response
    except httpx.HTTPError as e:
        logger.error(f"HTTP error communicating with Aegnt service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Error communicating with Aegnt service. Please ensure the service is running."
        )
    except ValueError as e:
        logger.error(f"Value error from Aegnt service: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error invoking agent: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request"
        )
