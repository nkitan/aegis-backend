
from fastapi import APIRouter, Depends, UploadFile, File
from models.user import User
from core.auth import get_current_user
from services.gemini_service import GeminiService
from services.firestore_service import FirestoreService
from services.google_wallet_service import GoogleWalletService
import googlemaps
from models.transaction import Transaction
from typing import List
from datetime import datetime
from core.config import settings

router = APIRouter()

gemini_service = GeminiService()
firestore_service = FirestoreService()
google_wallet_service = GoogleWalletService()
gmaps = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)

@router.post("/transactions/process")
def process_transaction(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    """
    Receives a file (image, pdf) from the client, orchestrates the entire ingestion pipeline.
    """
    # 1. Call Gemini Pro Vision for OCR and data extraction
    receipt_data = gemini_service.extract_from_receipt(file.file.read())

    # 2. Perform reasoning to categorize items
    categorized_items = gemini_service.categorize_items(receipt_data.get("items", []))
    receipt_data["items"] = categorized_items

    # 3. Save the structured data to Firestore
    # Handle the transaction date
    try:
        if "transaction_date" in receipt_data and receipt_data["transaction_date"]:
            # Try to parse the date from the receipt
            transaction_date = datetime.fromisoformat(receipt_data["transaction_date"].replace('Z', '+00:00'))
        else:
            transaction_date = datetime.now()
    except (ValueError, AttributeError):
        # If date parsing fails, use current time
        transaction_date = datetime.now()

    # Transform Gemini items format to match Transaction model
    processed_items = []
    items_list = receipt_data.get("items", [])
    
    # Handle case where no items are detected (common in UPI screenshots)
    if not items_list or len(items_list) == 0:
        # Create a generic item for UPI transactions
        total_amount = receipt_data.get("total_amount", 0.0)
        processed_items.append({
            "name": "Transaction Amount",
            "price": float(total_amount),
            "quantity": 1.0,
            "unit": None,
            "category": "Digital Payment",
            "original_price": None,
            "discount": None
        })
    else:
        for item in items_list:
            # Ensure all required fields have valid values
            item_name = item.get("name")
            if not item_name or item_name.strip() == "":
                item_name = "Unknown Item"
            
            processed_items.append({
                "name": item_name,
                "price": float(item.get("total_price", 0.0)),  # Use total_price as price
                "quantity": float(item.get("quantity", 1.0)),
                "unit": item.get("unit"),
                "category": item.get("category") or "Unknown",
                "original_price": float(item.get("unit_price")) if item.get("unit_price") else None,
                "discount": float(item.get("total_price", 0.0)) - float(item.get("unit_price", 0.0)) * float(item.get("quantity", 1.0)) if item.get("unit_price") else None
            })

    # Format location data into a string
    store_location = receipt_data.get("store_location", {})
    location_str = None
    if store_location:
        location_parts = []
        if store_location.get("address"): location_parts.append(store_location["address"])
        if store_location.get("city"): location_parts.append(store_location["city"])
        if store_location.get("state"): location_parts.append(store_location["state"])
        if store_location.get("postal_code"): location_parts.append(store_location["postal_code"])
        if store_location.get("country"): location_parts.append(store_location["country"])
        location_str = ", ".join(filter(None, location_parts))

    # Ensure all required fields have valid values with proper fallbacks
    store_name = receipt_data.get("store_name")
    if not store_name or store_name.strip() == "":
        # For UPI transactions, try to extract merchant from payment_method or use generic fallback
        payment_method = receipt_data.get("payment_method", "")
        if "UPI" in payment_method.upper() or "PAYTM" in payment_method.upper() or "GPAY" in payment_method.upper():
            store_name = "Digital Payment Transaction"
        else:
            store_name = "Unknown Merchant"

    transaction_data = {
        "user_id": current_user.uid,
        "store_name": store_name,
        "transaction_date": transaction_date,
        "items": processed_items,
        "total_amount": float(receipt_data.get("total_amount", 0.0)),
        "subtotal_amount": float(receipt_data.get("subtotal", 0.0)),
        "tax_amount": float(receipt_data.get("tax", 0.0)) if receipt_data.get("tax") else None,
        "discount_amount": float(receipt_data.get("tip", 0.0)) if receipt_data.get("tip") else None,
        "currency": receipt_data.get("currency") or "USD",
        "payment_method": receipt_data.get("payment_method") or "Unknown",
        "category": receipt_data.get("transaction_category") or "General",
        "location": location_str  # Now a properly formatted string
    }

    # Validate the data against the Transaction model
    try:
        transaction = Transaction(**transaction_data)
    except Exception as validation_error:
        # Log the validation error and the data that caused it
        print(f"Transaction validation error: {validation_error}")
        print(f"Transaction data: {transaction_data}")
        
        # Return a more helpful error response
        return {
            "status": "error",
            "message": "Failed to validate transaction data",
            "details": str(validation_error),
            "transaction_data": transaction_data
        }
    
    transaction_id = firestore_service.add_transaction(current_user.uid, transaction.model_dump())

    # 4. Enrich the data (e.g., with Google Maps location data)
    store_name = transaction_data.get("store_name")
    if store_name and not transaction_data.get("location"):  # Only lookup if we don't have a location
        geocode_result = gmaps.geocode(store_name)
        if geocode_result:
            location = geocode_result[0]['formatted_address']
            transaction_data["location"] = location
            # Update the transaction in Firestore with the enriched location data
            firestore_service.update_transaction(current_user.uid, transaction_id, {"location": location})

    # 5. Trigger the creation of a Google Wallet pass with ALL parsed data
    wallet_pass_url = None
    try:
        # Format the transaction date for the wallet pass
        if isinstance(transaction_data.get("transaction_date"), datetime):
            formatted_date = transaction_data["transaction_date"].strftime("%Y-%m-%d")
        else:
            # If it's already a string, use it as is
            formatted_date = str(transaction_data.get("transaction_date", datetime.now().strftime("%Y-%m-%d")))

        # Include ALL parsed data in the wallet pass
        wallet_pass_data = {
            "transaction_id": transaction_id,
            "store_name": transaction_data.get("store_name", "Unknown Store"),
            "total_amount": transaction_data.get("total_amount", 0.0),
            "subtotal_amount": transaction_data.get("subtotal_amount", 0.0),
            "tax_amount": transaction_data.get("tax_amount", 0.0),
            "discount_amount": transaction_data.get("discount_amount", 0.0),
            "transaction_date": formatted_date,
            "category": transaction_data.get("category", "General"),
            "currency": transaction_data.get("currency", "USD"),
            "payment_method": transaction_data.get("payment_method", "Unknown"),
            "items": processed_items,  # Include all items with full details
            "store_location": store_location if store_location else {},
            "location_string": transaction_data.get("location", "")
        }
        
        # Create the wallet pass with explicit pass type
        wallet_pass_url = google_wallet_service.create_pass(
            pass_type="transaction",
            pass_data=wallet_pass_data
        )
    except Exception as e:
        print(f"Warning: Failed to create wallet pass: {str(e)}")
        # Don't raise the error, as we still want to return the transaction data

    # Return comprehensive response including wallet pass URL
    response_data = {
        "status": "success", 
        "transaction_id": transaction_id,
        "transaction_data": transaction_data,
        "google_wallet_pass_url": wallet_pass_url
    }
    
    return response_data

@router.get("/transactions", response_model=List[Transaction])
def get_transactions(
    start_date: str,
    end_date: str,
    category: str = None,
    store_name: str = None,
    item_name: str = None,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves transaction data for the authenticated user.
    """
    return firestore_service.get_transactions(
        user_id=current_user.uid,
        start_date=start_date,
        end_date=end_date,
        category=category,
        store_name=store_name,
        item_name=item_name
    )
