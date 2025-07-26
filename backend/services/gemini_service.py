
import google.generativeai as genai
from core.config import settings
from PIL import Image
import io
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def extract_from_receipt(self, receipt_image: bytes) -> dict:
        """
        Uses Gemini Pro Vision to extract structured data from a receipt image.
        """
        image = Image.open(io.BytesIO(receipt_image))
        prompt = """Extract the following information from the receipt as a JSON object:
        {
            "store_name": "<store name>",
            "store_location": {
                "address": "<street address>",
                "city": "<city>",
                "state": "<state/province>",
                "postal_code": "<zip/postal code>",
                "country": "<country>",
                "phone": "<store phone if available>"
            },
            "transaction_date": "YYYY-MM-DDTHH:MM:SS",
            "currency": "<currency code: USD, EUR, GBP, etc.>",
            "items": [
                {
                    "name": "<item name>",
                    "quantity": <number of items>,
                    "unit_price": <price per unit>,
                    "total_price": <total price for this item>,
                    "category": "<category>"
                }
            ],
            "subtotal": <amount before tax/tips>,
            "tax": <tax amount>,
            "tip": <tip amount if applicable>,
            "total_amount": <final total amount>,
            "transaction_category": "<overall transaction category>",
            "payment_method": "<payment method if shown>"
        }

        Important instructions:
        1. If a field is not found, use null
        2. For currency, use standard 3-letter currency codes (USD, EUR, GBP, etc.)
        3. For quantities: 
           - If not explicitly stated, use 1
           - For weighted items (like produce), include the weight in the item name (e.g., "Apples 1.5 lbs")
        4. For item category, use general categories like: 'Groceries', 'Restaurant', 'Electronics', 'Clothing', 'Home', etc.
        5. For transaction_category, infer a single category that best describes the entire purchase
        6. Make sure unit_price × quantity equals total_price for each item
        7. Ensure all monetary values are numbers, not strings
        8. For store location:
           - Extract as much location detail as visible on the receipt
           - Format addresses according to local conventions
           - Use standard state/province codes where applicable (e.g., CA for California)
           - Use standard country codes (e.g., US, UK, CA)
           - Format phone numbers consistently with country conventions
        """
        response = self.model.generate_content([prompt, image])
        # Assuming the model returns a valid JSON string
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from Gemini API: {response.text}")
            return {
                "store_name": "Unknown",
                "transaction_date": "2024-01-01T00:00:00",
                "items": [],
                "total_amount": 0.0
            }

    def categorize_items(self, items: list) -> list:
        """
        Uses Gemini to categorize a list of items.
        """
        prompt = f"Categorize the following items into one of these categories: Groceries, Restaurant, Electronics, Clothing, Entertainment, Utilities, Transport, Health, Education, Other. Return a JSON array of objects with 'name' and 'category' fields. Items: {json.dumps(items)}"
        response = self.model.generate_content([prompt])
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print(f"Error decoding JSON from Gemini API for categorization: {response.text}")
            return items # Return original items if categorization fails
