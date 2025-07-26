import requests
import os

# Configuration
BASE_URL = "http://127.0.0.1:8000/api"
# It's recommended to use environment variables for sensitive data
FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY")
TEST_USER_EMAIL = os.environ.get("TEST_USER_EMAIL")
TEST_USER_PASSWORD = os.environ.get("TEST_USER_PASSWORD")

def get_firebase_id_token(email, password):
    """Authenticates with Firebase to get an ID token."""
    firebase_auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    try:
        response = requests.post(firebase_auth_url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()["idToken"]
    except requests.exceptions.RequestException as e:
        print(f"Error authenticating with Firebase: {e}")
        return None

def get_authenticated_header(token):
    """Returns the authorization header with the bearer token."""
    return {"Authorization": f"Bearer {token}"}

def get_user_profile(headers):
    """Tests the /users/me endpoint."""
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting user profile: {e}")
        return None

def invoke_agent(headers, prompt):
    """Tests the /agent/invoke endpoint."""
    try:
        response = requests.post(f"{BASE_URL}/agent/invoke", headers=headers, json={"prompt": prompt})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error invoking agent: {e}")
        return None

def main():
    """Main function to run the test client."""
    if not all([FIREBASE_API_KEY, TEST_USER_EMAIL, TEST_USER_PASSWORD]):
        print("Error: Please set FIREBASE_API_KEY, TEST_USER_EMAIL, and TEST_USER_PASSWORD environment variables.")
        return

    print("1. Authenticating with Firebase...")
    id_token = get_firebase_id_token(TEST_USER_EMAIL, TEST_USER_PASSWORD)
    if not id_token:
        return
    print("   Authentication successful.")

    headers = get_authenticated_header(id_token)

    print("\n2. Getting user profile...")
    user_profile = get_user_profile(headers)
    if user_profile:
        print(f"   User Profile: {user_profile}")

    print("\n3. Invoking the AI agent...")
    prompt = "How much did I spend on groceries last month?"
    print(f"   Prompt: {prompt}")
    agent_response = invoke_agent(headers, prompt)
    if agent_response:
        print(f"   Agent Response: {agent_response}")

if __name__ == "__main__":
    main()
