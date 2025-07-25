"""
Tool definitions for the Aegis Agent.

This file implements the Python functions that serve as tools for the Aegnt.
These functions are responsible for interacting with the backend API and other
services as required.
"""

import httpx
import json
from datetime import datetime, timedelta
import google.generativeai as genai
from config import BACKEND_API_BASE_URL, GEMINI_API_KEY, BACKEND_API_TOKEN

# Configure the Gemini API key
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def process_receipt(file_data: bytes, file_type: str, user_id: str) -> dict:
    """
    Initiates the processing of a new receipt. This tool takes the raw file data
    and the user's ID and sends it to the backend for the entire ingestion
    workflow, including OCR, categorization, data storage, and Wallet Pass creation.
    """
    with httpx.Client() as client:
        files = {'file': (f'receipt.{file_type.split("/")[-1]}', file_data, file_type)}
        data = {'user_id': user_id}
        headers = {}
        if BACKEND_API_TOKEN:
            headers['Authorization'] = f'Bearer {BACKEND_API_TOKEN}'
        
        try:
            response = client.post(
                f"{BACKEND_API_BASE_URL}/transactions/process",
                files=files,
                data=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting the backend: {e}"}


def create_wallet_pass(pass_type: str, pass_data: dict) -> dict:
    """
    Generates a Google Wallet pass by sending structured data to the backend.
    Use this for creating shopping lists or dynamic budget/warranty trackers
    based on a user's request.
    """
    with httpx.Client() as client:
        headers = {}
        if BACKEND_API_TOKEN:
            headers['Authorization'] = f'Bearer {BACKEND_API_TOKEN}'

        try:
            response = client.post(
                f"{BACKEND_API_BASE_URL}/wallet/pass",
                json={"pass_type": pass_type, "pass_data": pass_data},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting the backend: {e}"}


def create_calendar_event(event_data: dict) -> dict:
    """
    Creates a Google Calendar event for a warranty expiration or a return
    deadline by calling the backend service.
    """
    with httpx.Client() as client:
        headers = {}
        if BACKEND_API_TOKEN:
            headers['Authorization'] = f'Bearer {BACKEND_API_TOKEN}'

        try:
            response = client.post(
                f"{BACKEND_API_BASE_URL}/calendar/event",
                json=event_data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting the backend: {e}"}


def query_transactions(
    user_id: str,
    time_period: str,
    category: str = None,
    store_name: str = None,
    item_name: str = None,
) -> list:
    """
    A flexible tool to retrieve specific transaction data by querying the backend.
    This is the workhorse for most analytical user questions. You must first
    reason about the user's request to determine the correct parameters to use.
    """
    # Basic parsing of natural language time_period.
    # A more robust solution would use a dedicated NLP library.
    end_date = datetime.now()
    if "last month" in time_period:
        start_date = (end_date - timedelta(days=30)).strftime('%Y-%m-%d')
    elif "august 2024" in time_period.lower():
        start_date = "2024-08-01"
        end_date = "2024-08-31"
    else: # Default to last 7 days
        start_date = (end_date - timedelta(days=7)).strftime('%Y-%m-%d')
    
    end_date = end_date.strftime('%Y-%m-%d')

    with httpx.Client() as client:
        params = {
            "user_id": user_id,
            "start_date": start_date,
            "end_date": end_date,
        }
        if category:
            params["category"] = category
        if store_name:
            params["store_name"] = store_name
        if item_name:
            params["item_name"] = item_name
        
        headers = {}
        if BACKEND_API_TOKEN:
            headers['Authorization'] = f'Bearer {BACKEND_API_TOKEN}'

        try:
            response = client.get(
                f"{BACKEND_API_BASE_URL}/transactions",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return [{"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}]
        except httpx.RequestError as e:
            return [{"error": f"An error occurred while requesting the backend: {e}"}]


def get_spending_summary(query_text: str, user_id: str) -> dict:
    """
    Answers high-level financial questions like, 'Compare my grocery spending
    in May vs. June.' It synthesizes data from multiple queries to provide a
    comprehensive answer.
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured."}

    model = genai.GenerativeModel('gemini-pro')
    prompt = f"You are a financial analyst. The user wants to know: '{query_text}'.                Based on this query, determine the necessary parameters to call the                query_transactions tool. You should call the tool for each time period                or category mentioned in the user's query. Then, synthesize the                results into a natural language answer and provide a structured                data object for charting. For example, if the user asks to compare                spending in May and June, you should call query_transactions for each                month and then compare the results. Respond with a JSON object containing                'natural_language_answer' and 'structured_data'."

    try:
        # This is a conceptual implementation. In a real ADK application,
        # you would use the agent's reasoning capabilities to have it
        # call the query_transactions tool itself.
        # For this example, we simulate the analysis that the LLM would perform.

        # Simulate LLM analysis of the query to extract parameters
        # This is where the agent would decide which queries to make.
        # For "Compare my grocery spending in May vs. June":
        may_transactions = query_transactions(user_id, "may 2024", category="Groceries")
        june_transactions = query_transactions(user_id, "june 2024", category="Groceries")

        may_total = sum(t.get('amount', 0) for t in may_transactions if 'error' not in t)
        june_total = sum(t.get('amount', 0) for t in june_transactions if 'error' not in t)

        # Synthesize the answer
        natural_language_answer = f"Your grocery spending in June was ${june_total}, compared to ${may_total} in May."
        structured_data = {
            "chart_type": "bar",
            "labels": ["May", "June"],
            "datasets": [
                {
                    "label": "Grocery Spending",
                    "data": [may_total, june_total]
                }
            ]
        }
        return {
            "natural_language_answer": natural_language_answer,
            "structured_data": structured_data
        }

    except Exception as e:
        return {"error": f"An error occurred while generating the spending summary: {e}"}


def generate_recipe_suggestion(pantry_items: list, user_preferences: str = None) -> list:
    """
    Provides recipe ideas based on the items currently available in the user's
    'Virtual Pantry'. This is a creative task.
    """
    if not GEMINI_API_KEY:
        return [{"error": "GEMINI_API_KEY is not configured."}]

    model = genai.GenerativeModel('gemini-pro')
    prompt = f"Based on the following pantry items: {', '.join(pantry_items)}"
    if user_preferences:
        prompt += f" and considering these preferences: {user_preferences}"
    prompt += ", suggest some creative recipes."

    try:
        response = model.generate_content(prompt)
        # Basic parsing of the response. A more robust solution would be needed.
        recipes = response.text.split('\n')
        return [recipe.strip() for recipe in recipes if recipe.strip()]
    except Exception as e:
        return [{"error": f"An error occurred while generating recipe suggestions: {e}"}]


def run_proactive_analysis(user_id: str) -> dict:
    """
    Analyzes a user's recent spending to detect trends, identify subscription
    price hikes, or find upcoming warranty expirations. This tool is triggered
    by the backend scheduler.
    """
    recent_transactions = query_transactions(user_id, "last 30 days")
    
    if not recent_transactions or "error" in recent_transactions[0]:
        return {"insight_found": False, "insight_message": "Could not retrieve recent transactions."}

    if not GEMINI_API_KEY:
        return {"insight_found": False, "insight_message": "GEMINI_API_KEY is not configured."}

    model = genai.GenerativeModel('gemini-pro')
    prompt = f"You are a financial analyst. Analyze the following JSON data of recent transactions: \
               {json.dumps(recent_transactions)}. Look for spending trends, potential duplicate charges, \
               subscription price hikes (e.g., a recurring payment that has increased), or upcoming \
               warranty expirations (based on purchase dates). If you find a significant insight, \
               respond with a JSON object with 'insight_found' as true and a concise \
               'insight_message' to send to the user as a push notification. Otherwise, respond with \
               'insight_found' as false."

    try:
        response = model.generate_content(prompt)
        insight = json.loads(response.text)

        if insight.get("insight_found"):
            send_push_notification(user_id, insight["insight_message"])
            return insight
        else:
            return {"insight_found": False, "insight_message": "No new insights found."}

    except Exception as e:
        return {"insight_found": False, "insight_message": f"An error occurred during analysis: {e}"}


def generate_savings_plan(user_id: str, goal_amount: float, time_frame: str) -> dict:
    """
    Helps users with forward-looking problems by creating a personalized savings
    plan based on their spending history.
    """
    spending_history = query_transactions(user_id, "last 90 days")

    if not spending_history or "error" in spending_history[0]:
        return {"error": "Could not retrieve spending history."}

    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured."}

    model = genai.GenerativeModel('gemini-pro')
    prompt = f"You are a financial advisor. A user wants to save ${goal_amount} in {time_frame}. \
               Their spending history for the last 90 days is as follows (in JSON format): \
               {json.dumps(spending_history)}. \
               Analyze this spending history to identify categories where they can likely cut back. \
               Provide a personalized savings plan with a summary and a list of specific, actionable \
               suggestions. Respond with a JSON object containing 'summary' and 'suggestions'."

    try:
        response = model.generate_content(prompt)
        plan = json.loads(response.text)
        return plan
    except Exception as e:
        return {"error": f"An error occurred while generating the savings plan: {e}"}


def manage_savings_challenge(user_id: str, challenge_type: str, action: str) -> dict:
    """
    Manages opt-in gamified savings challenges by interacting with the backend.
    """
    with httpx.Client() as client:
        headers = {}
        if BACKEND_API_TOKEN:
            headers['Authorization'] = f'Bearer {BACKEND_API_TOKEN}'

        try:
            if action == "start":
                response = client.post(
                    f"{BACKEND_API_BASE_URL}/challenges",
                    json={"user_id": user_id, "challenge_type": challenge_type},
                    headers=headers
                )
            else: # check_progress or complete
                response = client.get(
                    f"{BACKEND_API_BASE_URL}/challenges",
                    params={"user_id": user_id, "action": action},
                    headers=headers
                )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting the backend: {e}"}


def send_push_notification(user_id: str, message: str) -> dict:
    """
    Sends a timely alert or insight to the user's device by calling the
    backend's notification service.
    """
    with httpx.Client() as client:
        headers = {}
        if BACKEND_API_TOKEN:
            headers['Authorization'] = f'Bearer {BACKEND_API_TOKEN}'

        try:
            response = client.post(
                f"{BACKEND_API_BASE_URL}/notifications/send",
                json={"user_id": user_id, "message": message},
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting the backend: {e}"}