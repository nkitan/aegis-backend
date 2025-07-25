# Project Aegis Setup Guide

This guide provides detailed instructions to set up and run both the `backend` and `aegnt` (Aegis Agent) components of Project Aegis.

## 1. Backend Setup

### 1.1. Google Cloud Project Setup

Before running the backend, you need to set up your Google Cloud Project and enable the necessary APIs.

#### 1.1.1. Create a Google Cloud Project
If you don't have one, create a new project in the Google Cloud Console.

#### 1.1.2. Enable Required APIs
Navigate to "APIs & Services" > "Enabled APIs & Services" in your Google Cloud Console and ensure the following APIs are enabled:

*   **Cloud Firestore API**
*   **Identity Toolkit API** (for Firebase Authentication)
*   **Google Wallet API**
*   **Google Calendar API**
*   **Google Maps Platform APIs** (specifically, Geocoding API for location enrichment)
*   **Cloud Vision API** (for Gemini Pro Vision, though Gemini API is used directly)
*   **Firebase Cloud Messaging API**

#### 1.1.3. Create Service Accounts & Download Keys

For secure access to Google Cloud services, you'll need to create service accounts and download their JSON key files.

*   **Firebase Admin SDK (for Authentication & FCM):**
    1.  Go to Firebase Console > Project settings > Service accounts.
    2.  Generate a new private key and download the JSON file. This file will be used for `GOOGLE_APPLICATION_CREDENTIALS` in `backend/core/config.py`.
*   **Google Wallet API:**
    1.  Go to Google Cloud Console > IAM & Admin > Service accounts.
    2.  Create a new service account with the "Google Wallet API Editor" role.
    3.  Generate a new JSON key for this service account. This file will be used for `GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE`.
*   **Google Calendar API:**
    1.  Go to Google Cloud Console > IAM & Admin > Service accounts.
    2.  Create a new service account with the "Calendar Editor" role.
    3.  Generate a new JSON key for this service account. This file will be used for `GOOGLE_CALENDAR_SERVICE_ACCOUNT_KEY_FILE`.

### 1.2. Configuration (`backend/core/config.py`)

Update the `backend/core/config.py` file with your specific credentials and API keys. **For production environments, it is highly recommended to use environment variables or Google Secret Manager instead of hardcoding these values.**

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

### 1.3. Google Wallet Pass Class Setup

Before you can create Google Wallet passes, you need to define a "Class" for your passes in the Google Wallet API console.

1.  **Access Google Wallet API Console:** Go to the [Google Wallet API Console](https://pay.google.com/gp/m/issuer/home).
2.  **Create a New Class:**
    *   For transaction receipts, you'll likely want to create a "Generic Pass" class.
    *   Configure the class with the fields and layout you desire (e.g., fields for store name, total amount, transaction date).
3.  **Obtain `classId`:** After creating the class, Google Wallet will assign it a unique `classId`. It will typically be in the format `issuerId.your_class_name`.
4.  **Update `backend/services/google_wallet_service.py`:** Replace the placeholder `f"{settings.GOOGLE_WALLET_ISSUER_ID}.transaction_class"` with your actual `classId` in the `create_pass` method.

### 1.4. Firebase Cloud Messaging (FCM) Token Handling

The backend sends push notifications via FCM. For this to work, your Flutter app needs to send the user's FCM token to the backend.

#### 1.4.1. In your Flutter App:

1.  **Initialize Firebase:** Ensure Firebase is correctly initialized in your Flutter project.
2.  **Get FCM Token:** Use the `firebase_messaging` package to obtain the device's FCM token:
    ```dart
    import 'package:firebase_messaging.dart';

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

#### 1.4.2. In the Backend (`backend/services/firebase_notification_service.py`):

*   The `send_notification` method now automatically retrieves the FCM token for the `user_id` from your Firestore database. Ensure that your Flutter app sends the FCM token to the backend as described in the previous step.

### 1.5. Running the Backend Server

Once all configurations are updated and dependencies are installed, you can run the FastAPI server.

1.  **Navigate to the Backend Directory:**
    ```bash
    cd backend
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

### 1.6. Deployment

For production, consider deploying your FastAPI application to a cloud platform like Google Cloud Run, Google Kubernetes Engine (GKE), or App Engine. Google Cloud Run is often a good choice for FastAPI due to its containerization support and serverless nature.

### 1.7. Testing

Thoroughly test all endpoints and integrations to ensure they function as expected. Pay special attention to:

*   **Authentication:** Verify that protected endpoints require a valid Firebase ID token.
*   **Transaction Processing:** Test with various receipt images/PDFs to ensure accurate data extraction, categorization, and Firestore storage.
*   **Google API Integrations:** Confirm that Google Wallet passes are created, Calendar events are scheduled, and notifications are sent successfully.
*   **Data Querying:** Test the `/transactions` endpoint with different query parameters.
*   **Savings Challenges:** Verify that challenges are created and retrieved correctly from Firestore.

## 2. Aegnt (Aegis Agent) Setup

### 2.1. Prerequisites

*   Python 3.9+ installed on your system.
*   Access to a Google Gemini API key.
*   A running backend server for the Aegis application (see Backend Setup above).

### 2.2. Setup Instructions

1.  **Navigate to the Aegnt Directory:**

    ```bash
    cd aegnt
    ```

2.  **Create and Activate a Python Virtual Environment:**

    It's highly recommended to use a virtual environment to manage dependencies.

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**

    Install the necessary Python packages.

    ```bash
    pip install -r requirements.txt
    ```
    *(Note: The original `RUN.md` suggested `pip install google-generativeai httpx google-adk`. We are assuming `requirements.txt` will contain these and any other necessary dependencies for a more robust setup.)*

4.  **Configure Environment Variables:**

    The agent requires certain environment variables to be set. You can set these in your shell session or create a `.env` file and use a tool like `python-dotenv` to load them.

    *   `BACKEND_API_BASE_URL`: The URL of your Aegis backend server (e.g., `http://localhost:8000`).
    *   `GEMINI_API_KEY`: Your Google Gemini API key.
    *   `BACKEND_API_TOKEN`: (Optional) An authentication token for your backend API, if required.

    Example (for shell session):

    ```bash
    export BACKEND_API_BASE_URL="http://localhost:8000"
    export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    # export BACKEND_API_TOKEN="YOUR_BACKEND_API_TOKEN" # Uncomment if needed
    ```

    Example (`.env` file):

    ```
    BACKEND_API_BASE_URL="http://localhost:8000"
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
    # BACKEND_API_TOKEN="YOUR_BACKEND_API_TOKEN"
    ```

5.  **Run the Agent:**

    Once the environment variables are set, you can run the agent:

    ```bash
    python main_agent.py
    ```

    The agent will start, and you can interact with it in your terminal. Type `exit` to end the conversation.

### 2.3. Interacting with the Agent

After running `python main_agent.py`, you will see a prompt. You can type your queries and instructions there. The agent will use its configured tools to respond.
