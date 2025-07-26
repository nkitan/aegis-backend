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
from typing import Optional, List, Dict, Any

# Configure the Gemini API key
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def process_receipt(file_data_base64: str, file_type: str, user_id: str, id_token: str) -> dict:
    """
    Initiates the processing of a new receipt. This tool takes the base64-encoded file data
    and the user's ID and sends it to the backend for the entire ingestion
    workflow, including OCR, categorization, data storage, and Wallet Pass creation.
    """
    import base64
    file_data = base64.b64decode(file_data_base64)
    with httpx.Client() as client:
        files = {'file': (f'receipt.{file_type.split("/")[-1]}', file_data, file_type)}
        data = {'user_id': user_id}
        headers = {'Authorization': f'Bearer {id_token}'}
        
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


def create_wallet_pass(pass_type: str, pass_data: dict, id_token: str) -> dict:
    """
    Generates a Google Wallet pass by sending structured data to the backend.
    Use this for creating shopping lists or dynamic budget/warranty trackers
    based on a user's request.
    """
    with httpx.Client() as client:
        headers = {'Authorization': f'Bearer {id_token}'}

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


def create_calendar_event(event_data: dict, id_token: str) -> dict:
    """
    Creates a Google Calendar event for a warranty expiration or a return
    deadline by calling the backend service.
    """
    with httpx.Client() as client:
        headers = {'Authorization': f'Bearer {id_token}'}

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
    id_token: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    store_name: Optional[str] = None,
    item_name: Optional[str] = None,
    currency: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    postal_code: Optional[str] = None,
) -> list:
    """
    A flexible tool to retrieve specific transaction data by querying the backend.
    This is the workhorse for most analytical user questions. You must first
    reason about the user's request to determine the correct parameters to use.
    """
    # Default to last 30 days if no dates are provided
    if not start_date and not end_date:
        end_date_obj = datetime.now()
        start_date_obj = end_date_obj - timedelta(days=30)
        start_date = start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date_obj.strftime('%Y-%m-%d')

    with httpx.Client() as client:
        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if category:
            params["category"] = category
        if store_name:
            params["store_name"] = store_name
        if item_name:
            params["item_name"] = item_name
        if currency:
            params["currency"] = currency
        if city:
            params["city"] = city
        if state:
            params["state"] = state
        if country:
            params["country"] = country
        if postal_code:
            params["postal_code"] = postal_code
        
        headers = {'Authorization': f'Bearer {id_token}'}

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


def summarize_transactions(transactions: list, query_text: str) -> dict:
    """
    Analyzes financial transaction data to answer user questions.
    
    Args:
        transactions: List of transaction dictionaries from query_transactions
        query_text: User's financial question or analysis request
        
    Returns:
        Dictionary with natural_language_answer and structured_data
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured."}

    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"You are a financial analyst. The user wants to know: '{query_text}'.                Analyze the following transaction data (in JSON format): {json.dumps(transactions)}.                Provide a natural language answer summarizing the relevant information                and a structured data object for charting. For example, if the user asks to compare                spending in May and June, you should compare the provided transactions for each                month and then compare the results. Respond with a JSON object containing                'natural_language_answer' and 'structured_data'."

    try:
        response = model.generate_content(prompt)
        summary = json.loads(response.text)
        return summary
    except Exception as e:
        return {"error": f"An error occurred while generating the spending summary: {e}"}


from config import SPOONACULAR_API_KEY

def generate_recipe_suggestion(pantry_items: list, user_preferences: Optional[str] = None) -> list:
    """
    Provides recipe ideas based on the items currently available in the user's
    'Virtual Pantry'. This is a creative task.
    
    Args:
        pantry_items: A list of ingredient strings
        user_preferences: Optional user preferences for recipes
        
    Returns:
        A list of recipe suggestions
    """
    if not SPOONACULAR_API_KEY:
        return [{"error": "SPOONACULAR_API_KEY is not configured."}]

    ingredients_str = ','.join(pantry_items)
    
    # Prioritize using as many given ingredients as possible (ranking=1)
    # and ignore common pantry items like water, salt, etc.
    params = {
        "ingredients": ingredients_str,
        "number": 5,  # Return up to 5 recipes
        "ranking": 1,
        "ignorePantry": True,
        "apiKey": SPOONACULAR_API_KEY
    }

    try:
        response = httpx.get("https://api.spoonacular.com/recipes/findByIngredients", params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        recipes_data = response.json()

        suggestions = []
        if recipes_data:
            for recipe in recipes_data:
                title = recipe.get("title")
                used_ingredients = ", ".join([ing["name"] for ing in recipe.get("usedIngredients", [])])
                missing_ingredients = ", ".join([ing["name"] for ing in recipe.get("missedIngredients", [])])
                
                suggestion = f"Recipe: {title}\n"
                suggestion += f"  Used Ingredients: {used_ingredients}\n"
                if missing_ingredients:
                    suggestion += f"  Missing Ingredients: {missing_ingredients}\n"
                suggestions.append(suggestion)
        else:
            suggestions.append("No recipes found with the given ingredients.")
            
        return suggestions
    except httpx.HTTPStatusError as e:
        return [{"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}]
    except httpx.RequestError as e:
        return [{"error": f"An error occurred while requesting the Spoonacular API: {e}"}]
    except Exception as e:
        return [{"error": f"An unexpected error occurred: {e}"}]


def run_proactive_analysis(user_id: str, id_token: str) -> dict:
    """
    Analyzes a user's recent spending to detect trends, identify subscription
    price hikes, or find upcoming warranty expirations. This tool is triggered
    by the backend scheduler.
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_transactions = query_transactions(user_id, id_token, start_date=start_date, end_date=end_date)
    
    if not recent_transactions or "error" in recent_transactions[0]:
        return {"insight_found": False, "insight_message": "Could not retrieve recent transactions."}

    if not GEMINI_API_KEY:
        return {"insight_found": False, "insight_message": "GEMINI_API_KEY is not configured."}

    model = genai.GenerativeModel('gemini-2.5-flash')
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
            send_push_notification(user_id, insight["insight_message"], id_token)
            return insight
        else:
            return {"insight_found": False, "insight_message": "No new insights found."}

    except Exception as e:
        return {"insight_found": False, "insight_message": f"An error occurred during analysis: {e}"}


def generate_savings_plan(user_id: str, goal_amount: float, time_frame: str, id_token: str) -> dict:
    """
    Helps users with forward-looking problems by creating a personalized savings
    plan based on their spending history.
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    spending_history = query_transactions(user_id, id_token, start_date=start_date, end_date=end_date)

    if not spending_history or "error" in spending_history[0]:
        return {"error": "Could not retrieve spending history."}

    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured."}

    model = genai.GenerativeModel('gemini-2.5-flash')
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


def manage_savings_challenge(user_id: str, challenge_type: str, action: str, id_token: str) -> dict:
    """
    Manages opt-in gamified savings challenges by interacting with the backend.
    """
    with httpx.Client() as client:
        headers = {'Authorization': f'Bearer {id_token}'}

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


def send_push_notification(user_id: str, message: str, id_token: str) -> dict:
    """
    Sends a timely alert or insight to the user's device by calling the
    backend's notification service.
    """
    with httpx.Client() as client:
        headers = {'Authorization': f'Bearer {id_token}'}

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