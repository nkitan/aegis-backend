
import google.generativeai as genai
from core.config import settings
from PIL import Image
import io
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

class GeminiService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def extract_from_receipt
        """
        Uses Gemini Pro Vision to extract structured data from a receipt image.
        """
        image = Image.open(io.BytesIO(receipt_image))
        prompt = """Extract the following information from the receipt as a JSON object:
        {
            "store_name": "<store name>",
            "transaction_date": "YYYY-MM-DDTHH:MM:SS",
            "items": [
                {"name": "<item name>", "price": <price>, "category": "<category>"}
            ],
            "total_amount": <total amount>,
            "transaction_category": "<overall transaction category>"
        }
        If a field is not found, use null. For item category, try to infer a general category like 'Groceries', 'Restaurant', 'Electronics', 'Clothing', etc. For overall transaction category, infer a single category that best describes the entire transaction.
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
