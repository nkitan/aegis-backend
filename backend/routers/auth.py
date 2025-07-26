from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from firebase_admin import auth
from pydantic import BaseModel

from models.user import User
from core.auth import get_current_user

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user():
    # This endpoint is a placeholder, as registration is handled by the Firebase client-side SDK.
    return {"message": "Please use the client-side Firebase SDK to register."}


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        # The form_data.username is the ID token from the client
        id_token = form_data.password
        decoded_token = auth.verify_id_token(id_token)
        return {"access_token": id_token, "token_type": "bearer"}
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
