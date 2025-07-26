
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from firebase_admin import auth, credentials
import firebase_admin
from core.config import settings
from models.user import User

# Initialize Firebase Admin SDK
# It's recommended to load credentials from a secure source, not hardcode them.
cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        decoded_token = auth.verify_id_token(token)
        return User(
            uid=decoded_token['uid'],
            email=decoded_token['email'],
            display_name=decoded_token.get('name'),
            id_token=token
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
