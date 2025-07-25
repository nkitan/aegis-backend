# Project Aegis Backend Setup Guide

This guide provides detailed instructions to get your Project Aegis backend fully functional and production-ready.

## 1. Google Cloud Project Setup

Before running the backend, you need to set up your Google Cloud Project and enable the necessary APIs.

### 1.1. Create a Google Cloud Project
If you don't have one, create a new project in the Google Cloud Console.

### 1.2. Enable Required APIs
Navigate to "APIs & Services" > "Enabled APIs & Services" in your Google Cloud Console and ensure the following APIs are enabled:

*   **Cloud Firestore API**
*   **Identity Toolkit API** (for Firebase Authentication)
*   **Google Wallet API**
*   **Google Calendar API**
*   **Google Maps Platform APIs** (specifically, Geocoding API for location enrichment)
*   **Cloud Vision API** (for Gemini Pro Vision, though Gemini API is used directly)
*   **Firebase Cloud Messaging API**

### 1.3. Create Service Accounts & Download Keys

For secure access to Google Cloud services, you'll need to create service accounts and download their JSON key files.

*   **Firebase Admin SDK (for Authentication & FCM):**
    1.  Go to Firebase Console > Project settings > Service accounts.
    2.  Generate a new private key and download the JSON file. This file will be used for `GOOGLE_APPLICATION_CREDENTIALS` in `core/config.py`.
*   **Google Wallet API:**
    1.  Go to Google Cloud Console > IAM & Admin > Service accounts.
    2.  Create a new service account with the "Google Wallet API Editor" role.
    3.  Generate a new JSON key for this service account. This file will be used for `GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE`.
*   **Google Calendar API:**
    1.  Go to Google Cloud Console > IAM & Admin > Service accounts.
    2.  Create a new service account with the "Calendar Editor" role.
    3.  Generate a new JSON key for this service account. This file will be used for `GOOGLE_CALENDAR_SERVICE_ACCOUNT_KEY_FILE`.

## 2. Configuration (`core/config.py`)

Update the `core/config.py` file with your specific credentials and API keys. **For production environments, it is highly recommended to use environment variables or Google Secret Manager instead of hardcoding these values.**

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Project Aegis Backend"
    API_V1_STR: str = "/api/v1"

    # Firebase Admin SDK / Google Cloud Application Credentials
    # Path to your Firebase service account key JSON file
    GOOGLE_APPLICATION_CREDENTIALS: str = "path/to/your/firebase_service_account.json"

    # Aegnt Agent API URL (if running separately)
    AEGNT_API_URL: str = "http://localhost:8001/api/v1" # Update if Aegnt agent is deployed elsewhere

    # Gemini API Key
    GEMINI_API_KEY: str = "your_gemini_api_key" # Obtain from Google AI Studio

    # Google Maps API Key
    GOOGLE_MAPS_API_KEY: str = "your_google_maps_api_key" # Obtain from Google Cloud Console

    # Google Wallet API Credentials
    GOOGLE_WALLET_ISSUER_ID: str = "your_google_wallet_issuer_id" # Your Issuer ID from Google Wallet API Console
    GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE: str = "path/to/your/google_wallet_service_account_key.json"

    # Google Calendar API Credentials
    GOOGLE_CALENDAR_SERVICE_ACCOUNT_KEY_FILE: str = "path/to/your/google_calendar_service_account_key.json"

    class Config:
        case_sensitive = True

settings = Settings()
```

## 3. Google Wallet Pass Class Setup

Before you can create Google Wallet passes, you need to define a "Class" for your passes in the Google Wallet API console.

1.  **Access Google Wallet API Console:** Go to the [Google Wallet API Console](https://pay.google.com/gp/m/issuer/home).
2.  **Create a New Class:**
    *   For transaction receipts, you'll likely want to create a "Generic Pass" class.
    *   Configure the class with the fields and layout you desire (e.g., fields for store name, total amount, transaction date).
3.  **Obtain `classId`:** After creating the class, Google Wallet will assign it a unique `classId`. It will typically be in the format `issuerId.your_class_name`.
4.  **Update `services/google_wallet_service.py`:** Replace the placeholder `f"{settings.GOOGLE_WALLET_ISSUER_ID}.transaction_class"` with your actual `classId` in the `create_pass` method.

## 4. Firebase Cloud Messaging (FCM) Token Handling

The backend sends push notifications via FCM. For this to work, your Flutter app needs to send the user's FCM token to the backend.

### 4.1. In your Flutter App:

1.  **Initialize Firebase:** Ensure Firebase is correctly initialized in your Flutter project.
2.  **Get FCM Token:** Use the `firebase_messaging` package to obtain the device's FCM token:
    ```dart
    import 'package:firebase_messaging/firebase_messaging.dart';

    final fcmToken = await FirebaseMessaging.instance.getToken();
    print('FCM Token: $fcmToken');
    ```
3.  **Send Token to Backend:** After obtaining the `fcmToken`, send it to your Project Aegis backend using the new endpoint:
    ```
    POST /api/v1/users/me/fcm_token
    Content-Type: application/json

    {
        "fcm_token": "YOUR_FCM_TOKEN_HERE"
    }
    ```
    This will store the token in your Firestore database, associated with the user's profile (`users/{user_id}`).

### 4.2. In the Backend (`services/firebase_notification_service.py`):

*   The `send_notification` method now automatically retrieves the FCM token for the `user_id` from your Firestore database. Ensure that your Flutter app sends the FCM token to the backend as described in the next step.

## 5. Running the Backend Server

Once all configurations are updated and dependencies are installed, you can run the FastAPI server.

1.  **Navigate to the Backend Directory:**
    ```bash
    cd /home/nkitan/Work/project-aegis/backend
    ```
2.  **Install Dependencies:** (If you haven't already or if you added new ones)
    ```bash
    pip install -r requirements.txt
    ```
3.  **Run the Server:**
    ```bash
    uvicorn main:app --reload
    ```
    *   `main:app` refers to the `app` object in `main.py`.
    *   `--reload` enables hot-reloading, which is useful for development.

## 6. Deployment

For production, consider deploying your FastAPI application to a cloud platform like Google Cloud Run, Google Kubernetes Engine (GKE), or App Engine. Google Cloud Run is often a good choice for FastAPI due to its containerization support and serverless nature.

## 7. Testing

Thoroughly test all endpoints and integrations to ensure they function as expected. Pay special attention to:

*   **Authentication:** Verify that protected endpoints require a valid Firebase ID token.
*   **Transaction Processing:** Test with various receipt images/PDFs to ensure accurate data extraction, categorization, and Firestore storage.
*   **Google API Integrations:** Confirm that Google Wallet passes are created, Calendar events are scheduled, and notifications are sent successfully.
*   **Data Querying:** Test the `/transactions` endpoint with different query parameters.
*   **Savings Challenges:** Verify that challenges are created and retrieved correctly from Firestore.

By following these steps, you will have a fully functional and robust Project Aegis backend.