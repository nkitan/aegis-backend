
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, credentials
import firebase_admin
from core.config import settings
from models.user import User

# Initialize Firebase Admin SDK
# It's recommended to load credentials from a secure source, not hardcode them.
cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred)

security = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    # TEMPORARY HACKATHON FIX: Skip authentication validation
    # In production, you should validate the Firebase ID token properly
    
    if credentials:
        try:
            token = credentials.credentials
            decoded_token = auth.verify_id_token(token)
            return User(
                uid=decoded_token['uid'],
                email=decoded_token['email'],
                display_name=decoded_token.get('name'),
                id_token=token
            )
        except auth.InvalidIdTokenError:
            # Fall through to default user for hackathon
            pass
    
    # Return a default test user for hackathon purposes
    return User(
        uid="vg21F4xzYJdg5yikFrEDAotLqli1",  # Default test user ID
        email="test@user.com",
        display_name="Test User",
        id_token="hackathon_bypass_token"
    )
