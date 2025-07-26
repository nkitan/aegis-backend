# Project Raseed: Frontend Technical Requirements

This document outlines the technical requirements for the Project Raseed frontend, built using Expo (React Native). It details the necessary API interactions, authentication handling, and data models required to build the application.

## 1. Authentication

The application uses Firebase Authentication. The frontend is responsible for managing the user sign-in/sign-up process and handling the Firebase ID token.

### 1.1. Authentication Flow

1.  **User Sign-in/Sign-up:** The frontend will provide UI for users to sign up or sign in using methods configured in Firebase (e.g., Google Sign-In, Email/Password).
2.  **Token Retrieval:** Upon successful authentication, the Firebase client-side SDK will provide a JSON Web Token (JWT) ID Token.
3.  **Token Storage:** The frontend must securely store this ID Token on the device. For Expo, `expo-secure-store` is recommended.
4.  **Authenticated Requests:** For all subsequent API calls to the backend, the frontend must include the ID Token in the `Authorization` header with the "Bearer" scheme.

    ```
    Authorization: Bearer <FIREBASE_ID_TOKEN>
    ```
5.  **Token Refresh:** The Firebase SDK manages token expiration and refresh automatically. The frontend should listen for token changes and update the stored token accordingly.
6.  **Logout:** On logout, the frontend must clear the stored ID Token and sign the user out of their Firebase session.

### 1.2. Authentication Endpoints

While user creation and sign-in are handled by the Firebase client SDK, the backend provides a token verification endpoint for testing and potential future use cases.

#### POST `/api/auth/token`

*   **Description:** This endpoint is used to validate a Firebase ID token and is primarily for backend testing. In the standard flow, the frontend acquires the token from Firebase directly.
*   **Request Body (`application/x-www-form-urlencoded`):**
    *   `password`: The Firebase ID Token.
    *   `username`: Can be left empty or contain the user's email (it is not used for validation in this flow).
*   **Response (200 OK):**
    ```json
    {
      "access_token": "string",
      "token_type": "bearer"
    }
    ```
*   **Error Response (401 Unauthorized):**
    ```json
    {
      "detail": "Invalid authentication credentials"
    }
    ```

## 2. API Endpoints & Data Models

The following sections detail the necessary API endpoints and the data structures for communication between the frontend and backend.

### 2.1. User Profile

#### GET `/api/users/me`

*   **Description:** Retrieves the profile of the currently authenticated user.
*   **Request:** None. The user is identified by the `Authorization` header.
*   **Response (200 OK):**
    ```json
    {
      "uid": "string",
      "email": "user@example.com",
      "display_name": "string"
    }
    ```

#### POST `/api/users/me/fcm_token`

*   **Description:** Updates the Firebase Cloud Messaging (FCM) token for the user to enable push notifications.
*   **Request Body:**
    ```json
    {
      "fcm_token": "string"
    }
    ```
*   **Response (200 OK):**
    ```json
    {
      "message": "FCM token updated successfully"
    }
    ```

### 2.2. Transactions (Receipts)

#### POST `/api/transactions/scan`

*   **Description:** Uploads a receipt image for processing and data extraction.
*   **Request Body (`multipart/form-data`):**
    *   `file`: The image file of the receipt.
*   **Response (200 OK):** Returns the created transaction object.
    ```json
    {
      "id": "string",
      "user_id": "string",
      "store_name": "string",
      "date": "YYYY-MM-DDTHH:MM:SS",
      "total_amount": 150.75,
      "items": [
        {
          "name": "string",
          "quantity": 1,
          "price": 25.00,
          "category": "string"
        }
      ]
    }
    ```

#### GET `/api/transactions`

*   **Description:** Retrieves a list of all transactions for the authenticated user.
*   **Request:** None.
*   **Response (200 OK):** An array of transaction objects.
    ```json
    [
      {
        "id": "string",
        "user_id": "string",
        "store_name": "string",
        "date": "YYYY-MM-DDTHH:MM:SS",
        "total_amount": 150.75,
        "items": [
          {
            "name": "string",
            "quantity": 1,
            "price": 25.00,
            "category": "string"
          }
        ]
      }
    ]
    ```

#### GET `/api/transactions/{transaction_id}`

*   **Description:** Retrieves a single transaction by its ID.
*   **Request:** None.
*   **Response (200 OK):** A single transaction object.
    ```json
    {
      "id": "string",
      "user_id": "string",
      "store_name": "string",
      "date": "YYYY-MM-DDTHH:MM:SS",
      "total_amount": 150.75,
      "items": [
        {
          "name": "string",
          "quantity": 1,
          "price": 25.00,
          "category": "string"
        }
      ]
    }
    ```

### 2.3. AI Financial Assistant

#### POST `/api/agent/invoke`

*   **Description:** Sends a natural language prompt to the AI financial assistant.
*   **Request Body:**
    ```json
    {
      "prompt": "string"
    }
    ```
*   **Response (200 OK):** The AI agent's response.
    ```json
    {
      "response": "string"
    }
    ```
