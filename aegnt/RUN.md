# How to Run the Aegis Agent (Aegnt)

This document outlines the steps required to set up and run the Aegis Agent.

## Prerequisites

*   Python 3.9+ installed on your system.
*   Access to a Google Gemini API key.
*   A running backend server for the Aegis application.

## Setup Instructions

1.  **Clone the Repository (if you haven't already):**

    ```bash
    git clone <repository_url>
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
    pip install google-generativeai httpx google-adk
    ```
    *Note: The `google-adk` package name is an assumption based on the imports. If this package is not found, please refer to the documentation for the Google Agent Development Kit (ADK) for the correct installation instructions.*

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

## Interacting with the Agent

After running `python main_agent.py`, you will see a prompt. You can type your queries and instructions there. The agent will use its configured tools to respond.
