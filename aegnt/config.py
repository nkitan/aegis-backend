"""
Configuration for the Aegis Agent.

This file stores configuration variables for the agent, such as API endpoints
and authentication credentials.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# The base URL for the backend API.
# Replace "http://localhost:8000" with the actual URL of your backend server.
BACKEND_API_BASE_URL = os.getenv("BACKEND_API_BASE_URL", "http://localhost:8000/api/v1")

# The API key for the Gemini API, used for generative tasks.
# It is recommended to set this as an environment variable for security.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Placeholder for a backend API token, if required for authentication.
BACKEND_API_TOKEN = os.getenv("BACKEND_API_TOKEN")

# The API key for the Spoonacular API, used for recipe suggestions.
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")