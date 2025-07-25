
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Aegis Backend"
    API_V1_STR: str = "/api/v1"
    # Add other settings like database credentials, secret keys, etc.
    # It's recommended to load these from environment variables or a secret manager.
    AEGNT_API_URL: str = os.getenv("AEGNT_API_URL", "<your_aegnt_api_url>")
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "<your_google_application_credentials_path>")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "<your_gemini_api_key>")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "<your_google_maps_api_key>")
    GOOGLE_WALLET_ISSUER_ID: str = os.getenv("GOOGLE_WALLET_ISSUER_ID", "your_google_wallet_issuer_id")
    GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE: str = os.getenv("GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE", "<your_google_wallet_service_account_key_file>")
    GOOGLE_CALENDAR_SERVICE_ACCOUNT_KEY_FILE: str = os.getenv("GOOGLE_CALENDAR_SERVICE_ACCOUNT_KEY_FILE", "<your_google_calendar_service_account_key_file>")

    class Config:
        case_sensitive = True

settings = Settings()
