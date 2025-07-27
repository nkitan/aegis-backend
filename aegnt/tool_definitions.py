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
    Helper function to retrieve transaction data from the backend database.
    Used internally by other analysis functions.
    """
    # Only apply default date range if BOTH start_date and end_date are None
    # This allows analyze_financial_data to control the date range properly
    if start_date is None and end_date is None:
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


def analyze_financial_data(
    user_id: str,
    id_token: str,
    query_text: str,
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
) -> dict:
    """
    Complete end-to-end financial analysis that retrieves data from database and provides insights.
    
    This function combines data retrieval and analysis to provide comprehensive financial insights
    based on the user's question and specified filters. It ONLY provides insights based on 
    actual transaction data from the user's database.
    
    Args:
        user_id: User identifier
        id_token: Authentication token
        query_text: User's financial question or analysis request
        start_date: Start date filter (YYYY-MM-DD format)
        end_date: End date filter (YYYY-MM-DD format)
        category: Transaction category filter
        store_name: Store name filter
        item_name: Item name filter
        currency: Currency filter
        city: City filter
        state: State filter
        country: Country filter
        postal_code: Postal code filter
        
    Returns:
        Complete analysis with transaction data, insights, and structured data for visualization
    """
    
    # Smart date range detection based on query text
    query_lower = query_text.lower()
    
    # For broad analytical queries, use a wider date range to capture all available data
    if any(phrase in query_lower for phrase in [
        "trends", "category", "categories", "most", "total", "all time", 
        "overall", "spending patterns", "store", "stores", "breakdown",
        "summary", "analysis", "compare", "comparison"
    ]):
        # Use a very wide date range to capture all historical data
        if not start_date and not end_date:
            start_date = "2015-01-01"  # Go back far enough to capture all data
            end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Handle specific time period queries
    elif "last month" in query_lower:
        end_date_obj = datetime.now().replace(day=1) - timedelta(days=1)  # Last day of previous month
        start_date_obj = end_date_obj.replace(day=1)  # First day of previous month
        start_date = start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date_obj.strftime('%Y-%m-%d')
    elif "this month" in query_lower:
        start_date_obj = datetime.now().replace(day=1)
        end_date_obj = datetime.now()
        start_date = start_date_obj.strftime('%Y-%m-%d')
        end_date = end_date_obj.strftime('%Y-%m-%d')
    elif any(year in query_lower for year in ["2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024", "2025"]):
        # Extract year from query
        import re
        year_match = re.search(r'\b(20\d{2})\b', query_lower)
        if year_match:
            year = year_match.group(1)
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
    
    # Smart category detection
    if not category:
        if any(word in query_lower for word in ["restaurant", "food", "dining", "eating"]):
            category = "Restaurant"
        elif any(word in query_lower for word in ["grocery", "groceries", "supermarket"]):
            category = "Grocery Store"
        elif any(word in query_lower for word in ["electronics", "tech", "mobile", "phone"]):
            category = "Electronics Store"
    
    # Step 1: Retrieve transaction data from database
    transactions = query_transactions(
        user_id=user_id,
        id_token=id_token,
        start_date=start_date,
        end_date=end_date,
        category=category,
        store_name=store_name,
        item_name=item_name,
        currency=currency,
        city=city,
        state=state,
        country=country,
        postal_code=postal_code
    )
    
    # Step 2: Check if data retrieval was successful
    if not transactions:
        return {
            "error": "No transaction data found for the specified criteria",
            "transactions": [],
            "analysis": {
                "natural_language_answer": f"I couldn't find any transactions matching your query '{query_text}' for the specified criteria. You may want to try a different date range or category.",
                "structured_data": {}
            },
            "query": query_text,
            "data_count": 0
        }
    
    if isinstance(transactions, list) and len(transactions) > 0 and "error" in transactions[0]:
        return {
            "error": transactions[0]["error"],
            "transactions": [],
            "analysis": {
                "natural_language_answer": f"I encountered an error while retrieving your transaction data: {transactions[0]['error']}",
                "structured_data": {}
            },
            "query": query_text,
            "data_count": 0
        }
    
    # Step 3: Perform analysis using Gemini with strict instructions
    if not GEMINI_API_KEY:
        return {
            "error": "GEMINI_API_KEY is not configured.",
            "transactions": transactions,
            "analysis": {
                "natural_language_answer": "I found your transaction data but cannot perform AI analysis due to configuration issues.",
                "structured_data": {}
            },
            "query": query_text,
            "data_count": len(transactions)
        }

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Enhanced prompt with better analysis instructions
    prompt = f"""You are a financial analyst. The user wants to know: '{query_text}'.

STRICT INSTRUCTIONS:
- ONLY analyze the provided transaction data below
- DO NOT make up or estimate any numbers
- Calculate exact amounts from the provided data
- Always specify the currency and time period of the data you're analyzing
- Provide specific transaction details when relevant
- For "most" queries (like "what store did I spend the most at"), analyze ALL transactions and find the actual maximum
- For "trends" or "category" queries, group and analyze the data by categories
- For "total" queries, sum up all relevant transactions

Analyze the following ACTUAL transaction data (in JSON format): {json.dumps(transactions, indent=2)}

Based ONLY on this real data, provide:
1. A comprehensive natural language answer that directly addresses the user's question with specific amounts, dates, and details from the data
2. Structured data for visualization (charts, graphs) based on the actual transactions

For example:
- If asked about "spending trends by category", group transactions by category and show totals
- If asked "what store did I spend the most at", find the store with highest total spending
- If asked about a specific time period, only include transactions from that period
- Always include actual numbers, dates, and store names from the data

Respond with a JSON object containing 'natural_language_answer' and 'structured_data'."""

    try:
        response = model.generate_content(prompt)
        
        # Clean up the response text to ensure it's valid JSON
        response_text = response.text.strip()
        
        # Try to find JSON content if the response has extra text
        if not response_text.startswith('{'):
            # Look for JSON content in the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            else:
                # If no JSON found, create a fallback response
                response_text = json.dumps({
                    "natural_language_answer": f"I found {len(transactions)} transactions from {start_date} to {end_date}, but couldn't parse the AI analysis. Here's a summary of your data.",
                    "structured_data": {"transaction_count": len(transactions)}
                })
        
        try:
            analysis_result = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing still fails
            analysis_result = {
                "natural_language_answer": f"I found {len(transactions)} transactions but encountered an issue parsing the detailed analysis. The data spans from {start_date} to {end_date}.",
                "structured_data": {"transaction_count": len(transactions)}
            }
        
        # Step 4: Return combined result with actual data
        return {
            "transactions": transactions,
            "analysis": analysis_result,
            "query": query_text,
            "data_count": len(transactions),
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "filters_applied": {
                "category": category,
                "store_name": store_name,
                "item_name": item_name,
                "currency": currency,
                "city": city,
                "state": state,
                "country": country,
                "postal_code": postal_code
            }
        }
    except Exception as e:
        return {
            "error": f"Analysis error: {e}",
            "transactions": transactions,
            "analysis": {
                "natural_language_answer": f"I found {len(transactions)} transactions from {transactions[0].get('transaction_date', 'N/A') if transactions else 'N/A'} to {transactions[-1].get('transaction_date', 'N/A') if transactions else 'N/A'}, but couldn't complete the AI analysis due to a technical error.",
                "structured_data": {"transaction_count": len(transactions)}
            },
            "query": query_text,
            "data_count": len(transactions)
        }


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

def get_virtual_pantry(user_id: str, id_token: str, days_back: int = 30) -> list[str]:
    """
    Automatically extracts pantry items from recent grocery and food purchases.
    
    Args:
        user_id: User identifier
        id_token: Authentication token
        days_back: Number of days to look back for purchases (default 30)
        
    Returns:
        List of ingredient strings from recent purchases
    """
    # Get recent transactions from grocery stores and food purchases
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    # Query for grocery and food-related purchases
    grocery_transactions = query_transactions(
        user_id=user_id,
        id_token=id_token,
        start_date=start_date,
        end_date=end_date,
        category="Grocery Store"
    )
    
    # Also get restaurant purchases for potential ingredients
    food_transactions = query_transactions(
        user_id=user_id,
        id_token=id_token,
        start_date=start_date,
        end_date=end_date,
        category="Restaurant"
    )
    
    pantry_items = set()
    
    # Extract ingredients from grocery transactions
    if grocery_transactions and not (len(grocery_transactions) > 0 and "error" in grocery_transactions[0]):
        for transaction in grocery_transactions:
            items = transaction.get("items", [])
            for item in items:
                item_name = item.get("name", "").lower()
                # Extract common pantry ingredients from item names
                pantry_items.update(extract_ingredients_from_item_name(item_name))
    
    # Extract ingredients from restaurant transactions (for inspiration)
    if food_transactions and not (len(food_transactions) > 0 and "error" in food_transactions[0]):
        for transaction in food_transactions:
            items = transaction.get("items", [])
            for item in items:
                item_name = item.get("name", "").lower()
                # Extract common ingredients from restaurant dishes
                pantry_items.update(extract_ingredients_from_item_name(item_name))
    
    return list(pantry_items)


def extract_ingredients_from_item_name(item_name: str) -> set[str]:
    """
    Helper function to extract likely ingredients from item names.
    
    Args:
        item_name: Name of the purchased item
        
    Returns:
        Set of ingredient strings
    """
    item_name = item_name.lower()
    ingredients = set()
    
    # Common ingredient mappings
    ingredient_keywords = {
        "tomato": ["tomato", "tomatoes"],
        "onion": ["onion", "onions", "pyaaz"],
        "rice": ["rice", "basmati", "jasmine rice"],
        "chicken": ["chicken", "poultry"],
        "garlic": ["garlic", "lehsun"],
        "potato": ["potato", "potatoes", "aloo", "batata"],
        "ginger": ["ginger", "adrak"],
        "lemon": ["lemon", "lime", "nimbu"],
        "spinach": ["spinach", "palak"],
        "paneer": ["paneer", "cottage cheese"],
        "yogurt": ["yogurt", "curd", "dahi"],
        "milk": ["milk", "dairy"],
        "bread": ["bread", "roti", "naan", "pav"],
        "flour": ["flour", "atta", "maida"],
        "oil": ["oil", "cooking oil", "olive oil"],
        "salt": ["salt", "namak"],
        "sugar": ["sugar", "cheeni"],
        "tea": ["tea", "chai"],
        "coffee": ["coffee"],
        "eggs": ["egg", "eggs", "anda"],
        "fish": ["fish", "machli"],
        "mutton": ["mutton", "lamb", "goat"],
        "prawns": ["prawn", "prawns", "shrimp"],
        "dal": ["dal", "lentils", "moong", "masoor", "chana"],
        "beans": ["beans", "rajma", "black beans"],
        "peas": ["peas", "matar"],
        "carrot": ["carrot", "carrots", "gajar"],
        "capsicum": ["capsicum", "bell pepper", "shimla mirch"],
        "cucumber": ["cucumber", "kheera"],
        "coriander": ["coriander", "cilantro", "dhania"],
        "mint": ["mint", "pudina"],
        "chili": ["chili", "chilli", "mirch", "pepper"],
        "coconut": ["coconut", "nariyal"],
        "cashew": ["cashew", "kaju"],
        "almond": ["almond", "badam"],
        "apple": ["apple", "seb"],
        "banana": ["banana", "kela"],
        "mango": ["mango", "aam"],
        "grapes": ["grapes", "angoor"]
    }
    
    # Check for ingredient keywords in the item name
    for ingredient, keywords in ingredient_keywords.items():
        for keyword in keywords:
            if keyword in item_name:
                ingredients.add(ingredient)
                break
    
    return ingredients


def generate_recipe_suggestion(user_id: str, id_token: str, user_preferences: Optional[str] = None, pantry_items: Optional[list[str]] = None) -> dict:
    """
    Provides recipe ideas based on the items currently available in the user's
    Virtual Pantry (automatically detected from recent purchases).
    
    Args:
        user_id: User identifier  
        id_token: Authentication token
        user_preferences: Optional user preferences for recipes
        pantry_items: Optional manual pantry items (if not provided, will auto-detect from purchases)
        
    Returns:
        A dictionary containing recipe suggestions and pantry items used
    """
    if not SPOONACULAR_API_KEY:
        return {"error": "SPOONACULAR_API_KEY is not configured."}
    
    # Auto-detect pantry items from recent purchases if not provided
    if not pantry_items:
        pantry_items = get_virtual_pantry(user_id, id_token)
        
    if not pantry_items:
        return {
            "error": "No pantry items found in recent purchases",
            "message": "I couldn't find any grocery items in your recent purchases to suggest recipes. Try uploading some grocery receipts first!",
            "pantry_items": []
        }

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
                suggestion += f"  Used Ingredients from your pantry: {used_ingredients}\n"
                if missing_ingredients:
                    suggestion += f"  Missing Ingredients: {missing_ingredients}\n"
                suggestions.append(suggestion)
        else:
            suggestions.append("No recipes found with the ingredients from your recent purchases.")
            
        return {
            "recipes": suggestions, 
            "count": len(suggestions),
            "pantry_items": pantry_items,
            "message": f"Found {len(pantry_items)} ingredients from your recent grocery purchases: {', '.join(pantry_items)}"
        }
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
    except httpx.RequestError as e:
        return {"error": f"An error occurred while requesting the Spoonacular API: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


def run_proactive_analysis(user_id: str, id_token: str) -> dict:
    """
    Analyzes a user's recent spending to detect trends, identify subscription
    price hikes, unusual spending patterns, or find upcoming warranty expirations. 
    This tool performs comprehensive proactive financial analysis.
    """
    if not GEMINI_API_KEY:
        return {"insight_found": False, "insight_message": "GEMINI_API_KEY is not configured."}

    # Get current month transactions
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_transactions = query_transactions(user_id, id_token, start_date=start_date, end_date=end_date)
    
    # Get previous month for comparison
    prev_end_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    prev_start_date = (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
    previous_transactions = query_transactions(user_id, id_token, start_date=prev_start_date, end_date=prev_end_date)
    
    # Validate transaction data
    if not recent_transactions or (isinstance(recent_transactions, list) and len(recent_transactions) > 0 and "error" in recent_transactions[0]):
        return {"insight_found": False, "insight_message": "Could not retrieve recent transactions for analysis."}
    
    if len(recent_transactions) < 3:
        return {"insight_found": False, "insight_message": "Insufficient transaction data for meaningful analysis."}

    # Prepare analysis data
    analysis_data = {
        "recent_transactions": recent_transactions,
        "previous_transactions": previous_transactions if previous_transactions and not (isinstance(previous_transactions, list) and len(previous_transactions) > 0 and "error" in previous_transactions[0]) else [],
        "analysis_period": f"{start_date} to {end_date}",
        "comparison_period": f"{prev_start_date} to {prev_end_date}" if previous_transactions else None
    }

    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Enhanced prompt for better insights
    prompt = f"""You are an expert financial analyst specializing in proactive spending insights.

ANALYSIS DATA:
Current Period ({start_date} to {end_date}): {json.dumps(recent_transactions, indent=2)}
Previous Period ({prev_start_date} to {prev_end_date}): {json.dumps(analysis_data["previous_transactions"], indent=2)}

ANALYSIS TASKS:
1. **Subscription Analysis**: Look for recurring payments and identify any price increases
2. **Spending Pattern Changes**: Compare current vs previous period spending by category
3. **Unusual Transactions**: Identify transactions that are significantly higher than normal
4. **Duplicate Charges**: Find potential duplicate transactions on the same day/amount
5. **Warranty Tracking**: Find items purchased 11-12 months ago that may have warranties expiring soon
6. **Budget Alerts**: Identify categories where spending has increased by >20%

RESPONSE FORMAT:
Respond with a JSON object containing:
- "insight_found": boolean (true if significant insight found)
- "insight_message": string (concise notification message for user, max 150 characters)
- "insight_type": string (one of: "subscription_increase", "spending_spike", "duplicate_charge", "warranty_expiring", "budget_alert", "unusual_pattern")
- "details": object with specific details about the insight
- "action_recommended": string (what the user should do about this insight)

CRITERIA FOR SIGNIFICANT INSIGHTS:
- Subscription price increases of any amount
- Category spending increases >25% from previous period
- Single transactions >$100 that are unusual for the user
- Duplicate transactions within 24 hours
- Warranties expiring in next 30 days
- Total spending increase >30% from previous period

Only report ONE most significant insight. If no significant insights found, return insight_found: false."""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response for JSON parsing
        if not response_text.startswith('{'):
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                response_text = json_match.group(0)
            else:
                return {"insight_found": False, "insight_message": "Failed to parse analysis response."}
        
        try:
            insight = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback analysis if JSON parsing fails
            return _fallback_proactive_analysis(recent_transactions, previous_transactions)
        
        # Validate response structure
        if not isinstance(insight, dict) or "insight_found" not in insight:
            return _fallback_proactive_analysis(recent_transactions, previous_transactions)
        
        # Send notification if insight found
        if insight.get("insight_found", False):
            notification_result = send_push_notification(user_id, insight.get("insight_message", "New financial insight available"), id_token)
            insight["notification_sent"] = notification_result.get("success", False)
            
            # Add metadata
            insight["analysis_timestamp"] = datetime.now().isoformat()
            insight["transaction_count"] = len(recent_transactions)
            
            return insight
        else:
            return {
                "insight_found": False, 
                "insight_message": "No significant insights found in recent spending patterns.",
                "analysis_timestamp": datetime.now().isoformat(),
                "transaction_count": len(recent_transactions)
            }

    except Exception as e:
        return {"insight_found": False, "insight_message": f"Analysis error: {str(e)[:100]}..."}


def _fallback_proactive_analysis(recent_transactions: list, previous_transactions: list) -> dict:
    """
    Fallback analysis when AI response parsing fails.
    Performs basic rule-based analysis to find obvious insights.
    """
    try:
        # Basic spending comparison
        if previous_transactions:
            recent_total = sum(float(t.get("total_amount", 0)) for t in recent_transactions)
            previous_total = sum(float(t.get("total_amount", 0)) for t in previous_transactions)
            
            if previous_total > 0:
                increase_percent = ((recent_total - previous_total) / previous_total) * 100
                
                if increase_percent > 30:
                    return {
                        "insight_found": True,
                        "insight_message": f"Spending increased {increase_percent:.0f}% from last month",
                        "insight_type": "spending_spike",
                        "details": {"recent_total": recent_total, "previous_total": previous_total}
                    }
        
        # Look for duplicate transactions
        amounts_dates = {}
        for transaction in recent_transactions:
            amount = float(transaction.get("total_amount", 0))
            date = transaction.get("transaction_date", "")
            store = transaction.get("store_name", "")
            key = f"{amount}_{date}_{store}"
            
            if key in amounts_dates:
                return {
                    "insight_found": True,
                    "insight_message": f"Possible duplicate charge: ${amount} at {store}",
                    "insight_type": "duplicate_charge",
                    "details": {"amount": amount, "store": store, "date": date}
                }
            amounts_dates[key] = True
        
        # Look for unusually large transactions
        amounts = [float(t.get("total_amount", 0)) for t in recent_transactions]
        if amounts:
            avg_amount = sum(amounts) / len(amounts)
            max_amount = max(amounts)
            
            if max_amount > avg_amount * 3 and max_amount > 100:
                large_transaction = next(t for t in recent_transactions if float(t.get("total_amount", 0)) == max_amount)
                return {
                    "insight_found": True,
                    "insight_message": f"Large transaction: ${max_amount:.2f} at {large_transaction.get('store_name', 'Unknown')}",
                    "insight_type": "unusual_pattern",
                    "details": {"amount": max_amount, "average": avg_amount}
                }
        
        return {"insight_found": False, "insight_message": "No significant patterns detected"}
        
    except Exception as e:
        return {"insight_found": False, "insight_message": f"Fallback analysis failed: {str(e)}"}


def run_comprehensive_proactive_analysis(user_id: str, id_token: str, analysis_days: int = 90) -> dict:
    """
    Runs a comprehensive proactive analysis over a longer period to identify
    more complex patterns and trends.
    
    Args:
        user_id: User identifier
        id_token: Authentication token  
        analysis_days: Number of days to analyze (default 90)
        
    Returns:
        Dictionary with multiple insights categorized by type
    """
    if not GEMINI_API_KEY:
        return {"error": "GEMINI_API_KEY is not configured."}
    
    # Get extended transaction history
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=analysis_days)).strftime('%Y-%m-%d')
    
    all_transactions = query_transactions(user_id, id_token, start_date=start_date, end_date=end_date)
    
    if not all_transactions or (isinstance(all_transactions, list) and len(all_transactions) > 0 and "error" in all_transactions[0]):
        return {"error": "Could not retrieve transaction history for comprehensive analysis."}
    
    insights = {
        "analysis_period": f"{start_date} to {end_date}",
        "total_transactions": len(all_transactions),
        "insights": []
    }
    
    # 1. Subscription Analysis
    subscription_insights = _analyze_subscriptions(all_transactions)
    if subscription_insights:
        insights["insights"].extend(subscription_insights)
    
    # 2. Category Trend Analysis  
    category_insights = _analyze_category_trends(all_transactions)
    if category_insights:
        insights["insights"].extend(category_insights)
    
    # 3. Merchant Analysis
    merchant_insights = _analyze_merchant_patterns(all_transactions)
    if merchant_insights:
        insights["insights"].extend(merchant_insights)
    
    # 4. Seasonal Analysis
    seasonal_insights = _analyze_seasonal_patterns(all_transactions)
    if seasonal_insights:
        insights["insights"].extend(seasonal_insights)
    
    # 5. Anomaly Detection
    anomaly_insights = _detect_spending_anomalies(all_transactions)
    if anomaly_insights:
        insights["insights"].extend(anomaly_insights)
    
    insights["insight_count"] = len(insights["insights"])
    insights["analysis_timestamp"] = datetime.now().isoformat()
    
    return insights


def _analyze_subscriptions(transactions: list) -> list:
    """Analyze transactions for subscription patterns and price changes."""
    insights = []
    
    # Group transactions by merchant and amount
    merchant_amounts = {}
    for transaction in transactions:
        merchant = transaction.get("store_name", "")
        amount = float(transaction.get("total_amount", 0))
        date = transaction.get("transaction_date", "")
        
        if merchant not in merchant_amounts:
            merchant_amounts[merchant] = []
        merchant_amounts[merchant].append({"amount": amount, "date": date})
    
    # Look for recurring patterns
    for merchant, transactions_list in merchant_amounts.items():
        if len(transactions_list) >= 3:  # At least 3 transactions to detect pattern
            amounts = [t["amount"] for t in transactions_list]
            dates = [t["date"] for t in transactions_list]
            
            # Check for amount variations (potential price increases)
            unique_amounts = list(set(amounts))
            if len(unique_amounts) > 1:
                min_amount = min(unique_amounts)
                max_amount = max(unique_amounts)
                
                if max_amount > min_amount * 1.1:  # 10% increase threshold
                    insights.append({
                        "type": "subscription_price_increase",
                        "merchant": merchant,
                        "old_amount": min_amount,
                        "new_amount": max_amount,
                        "increase_percent": ((max_amount - min_amount) / min_amount) * 100,
                        "message": f"{merchant} subscription increased from ${min_amount:.2f} to ${max_amount:.2f}"
                    })
    
    return insights


def _analyze_category_trends(transactions: list) -> list:
    """Analyze spending trends by category over time."""
    insights = []
    
    # Group by category and month
    from collections import defaultdict
    monthly_category_spending = defaultdict(lambda: defaultdict(float))
    
    for transaction in transactions:
        category = transaction.get("category", "Other")
        amount = float(transaction.get("total_amount", 0))
        date = transaction.get("transaction_date", "")
        
        if date:
            try:
                month = date[:7]  # YYYY-MM format
                monthly_category_spending[category][month] += amount
            except:
                continue
    
    # Analyze trends for each category
    for category, monthly_data in monthly_category_spending.items():
        if len(monthly_data) >= 2:
            months = sorted(monthly_data.keys())
            amounts = [monthly_data[month] for month in months]
            
            # Calculate trend
            if len(amounts) >= 2:
                recent_avg = sum(amounts[-2:]) / 2
                older_avg = sum(amounts[:-2]) / max(1, len(amounts) - 2) if len(amounts) > 2 else amounts[0]
                
                if recent_avg > older_avg * 1.25:  # 25% increase
                    insights.append({
                        "type": "category_spending_increase",
                        "category": category,
                        "old_average": older_avg,
                        "new_average": recent_avg,
                        "increase_percent": ((recent_avg - older_avg) / older_avg) * 100,
                        "message": f"{category} spending increased {((recent_avg - older_avg) / older_avg) * 100:.0f}%"
                    })
    
    return insights


def _analyze_merchant_patterns(transactions: list) -> list:
    """Analyze merchant spending patterns."""
    insights = []
    
    merchant_spending = {}
    for transaction in transactions:
        merchant = transaction.get("store_name", "")
        amount = float(transaction.get("total_amount", 0))
        
        if merchant not in merchant_spending:
            merchant_spending[merchant] = {"total": 0, "count": 0, "amounts": []}
        
        merchant_spending[merchant]["total"] += amount
        merchant_spending[merchant]["count"] += 1
        merchant_spending[merchant]["amounts"].append(amount)
    
    # Find top spending merchants
    top_merchants = sorted(merchant_spending.items(), key=lambda x: x[1]["total"], reverse=True)[:5]
    
    for merchant, data in top_merchants:
        if data["total"] > 200:  # Significant spending threshold
            avg_transaction = data["total"] / data["count"]
            insights.append({
                "type": "top_merchant",
                "merchant": merchant,
                "total_spent": data["total"],
                "transaction_count": data["count"],
                "average_transaction": avg_transaction,
                "message": f"Top spending: ${data['total']:.2f} at {merchant} ({data['count']} transactions)"
            })
    
    return insights


def _analyze_seasonal_patterns(transactions: list) -> list:
    """Analyze seasonal spending patterns."""
    insights = []
    
    # This is a simplified seasonal analysis
    # In a real implementation, you'd want more sophisticated time series analysis
    monthly_spending = {}
    
    for transaction in transactions:
        date = transaction.get("transaction_date", "")
        amount = float(transaction.get("total_amount", 0))
        
        if date:
            try:
                month = int(date.split("-")[1])
                if month not in monthly_spending:
                    monthly_spending[month] = []
                monthly_spending[month].append(amount)
            except:
                continue
    
    # Calculate average spending by month
    monthly_averages = {}
    for month, amounts in monthly_spending.items():
        monthly_averages[month] = sum(amounts) / len(amounts)
    
    if len(monthly_averages) >= 3:
        overall_avg = sum(monthly_averages.values()) / len(monthly_averages)
        
        for month, avg in monthly_averages.items():
            if avg > overall_avg * 1.3:  # 30% above average
                month_names = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                insights.append({
                    "type": "seasonal_high_spending",
                    "month": month,
                    "month_name": month_names[month],
                    "average_spending": avg,
                    "overall_average": overall_avg,
                    "message": f"High spending in {month_names[month]}: ${avg:.2f} vs ${overall_avg:.2f} average"
                })
    
    return insights


def _detect_spending_anomalies(transactions: list) -> list:
    """Detect unusual spending patterns or anomalies."""
    insights = []
    
    amounts = [float(t.get("total_amount", 0)) for t in transactions]
    
    if amounts:
        # Calculate statistics
        avg_amount = sum(amounts) / len(amounts)
        sorted_amounts = sorted(amounts)
        
        # Find outliers (simple method)
        q1_index = len(sorted_amounts) // 4
        q3_index = 3 * len(sorted_amounts) // 4
        
        if q1_index < len(sorted_amounts) and q3_index < len(sorted_amounts):
            q1 = sorted_amounts[q1_index]
            q3 = sorted_amounts[q3_index]
            iqr = q3 - q1
            
            upper_bound = q3 + 1.5 * iqr
            
            # Find anomalous transactions
            anomalous_transactions = [t for t in transactions if float(t.get("total_amount", 0)) > upper_bound]
            
            if anomalous_transactions:
                for transaction in anomalous_transactions[:3]:  # Limit to top 3 anomalies
                    amount = float(transaction.get("total_amount", 0))
                    merchant = transaction.get("store_name", "Unknown")
                    date = transaction.get("transaction_date", "")
                    
                    insights.append({
                        "type": "spending_anomaly",
                        "amount": amount,
                        "merchant": merchant,
                        "date": date,
                        "average_amount": avg_amount,
                        "message": f"Unusual transaction: ${amount:.2f} at {merchant} (avg: ${avg_amount:.2f})"
                    })
    
    return insights


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


def schedule_proactive_insights(user_id: str, id_token: str, frequency: str = "daily") -> dict:
    """
    Schedules proactive insight analysis for a user.
    
    Args:
        user_id: User identifier
        id_token: Authentication token
        frequency: How often to run analysis ("daily", "weekly", "monthly")
        
    Returns:
        Dictionary with scheduling result
    """
    with httpx.Client() as client:
        headers = {'Authorization': f'Bearer {id_token}'}
        
        try:
            response = client.post(
                f"{BACKEND_API_BASE_URL}/insights/schedule",
                json={
                    "user_id": user_id,
                    "frequency": frequency,
                    "analysis_type": "proactive"
                },
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting the backend: {e}"}


def get_user_insights_history(user_id: str, id_token: str, days_back: int = 30) -> dict:
    """
    Retrieves the history of insights generated for a user.
    
    Args:
        user_id: User identifier
        id_token: Authentication token
        days_back: Number of days to look back for insights
        
    Returns:
        Dictionary with insights history
    """
    with httpx.Client() as client:
        headers = {'Authorization': f'Bearer {id_token}'}
        params = {"days_back": days_back}
        
        try:
            response = client.get(
                f"{BACKEND_API_BASE_URL}/insights/history",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error occurred: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            return {"error": f"An error occurred while requesting the backend: {e}"}


def run_batch_proactive_analysis(user_ids: list, batch_size: int = 10) -> dict:
    """
    Runs proactive analysis for multiple users in batches.
    This would typically be called by a background scheduler.
    
    Args:
        user_ids: List of user IDs to analyze
        batch_size: Number of users to process in each batch
        
    Returns:
        Dictionary with batch processing results
    """
    results = {
        "total_users": len(user_ids),
        "processed": 0,
        "insights_found": 0,
        "errors": 0,
        "batch_results": []
    }
    
    # Process users in batches
    for i in range(0, len(user_ids), batch_size):
        batch = user_ids[i:i + batch_size]
        batch_result = {"batch_number": i // batch_size + 1, "users": []}
        
        for user_id in batch:
            try:
                # Note: In a real implementation, you'd need to get the id_token for each user
                # This is a simplified version
                insight_result = run_proactive_analysis(user_id, "system_token")
                
                batch_result["users"].append({
                    "user_id": user_id,
                    "success": True,
                    "insight_found": insight_result.get("insight_found", False),
                    "insight_type": insight_result.get("insight_type", None)
                })
                
                results["processed"] += 1
                if insight_result.get("insight_found", False):
                    results["insights_found"] += 1
                    
            except Exception as e:
                batch_result["users"].append({
                    "user_id": user_id,
                    "success": False,
                    "error": str(e)
                })
                results["errors"] += 1
        
        results["batch_results"].append(batch_result)
    
    results["completion_timestamp"] = datetime.now().isoformat()
    return results