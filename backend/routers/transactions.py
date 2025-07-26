
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

    transaction_data = {
        "user_id": current_user.uid,
        "transaction_date": transaction_date,
        **receipt_data
    }
    transaction_id = firestore_service.add_transaction(current_user.uid, transaction_data)

    # 4. Enrich the data (e.g., with Google Maps location data)
    store_name = transaction_data.get("store_name")
    if store_name:
        geocode_result = gmaps.geocode(store_name)
        if geocode_result:
            location = geocode_result[0]['formatted_address']
            transaction_data["location"] = location
            # Update the transaction in Firestore with the enriched location data
            firestore_service.update_transaction(current_user.uid, transaction_id, {"location": location})

    # 5. Trigger the creation of a Google Wallet pass
    try:
        # Format the transaction date for the wallet pass
        if isinstance(transaction_data.get("transaction_date"), datetime):
            formatted_date = transaction_data["transaction_date"].isoformat()
        else:
            # If it's already a string, use it as is
            formatted_date = str(transaction_data.get("transaction_date", datetime.now().isoformat()))

        wallet_pass_data = {
            "transaction_id": transaction_id,
            "store_name": transaction_data.get("store_name"),
            "total_amount": transaction_data.get("total_amount"),
            "transaction_date": formatted_date,
            "category": transaction_data.get("category"),
            "location": transaction_data.get("location", transaction_data.get("store_location", {}))
        }
        
        # Create the wallet pass with explicit pass type
        google_wallet_service.create_pass(
            pass_type="transaction",
            pass_data=wallet_pass_data
        )
    except Exception as e:
        print(f"Warning: Failed to create wallet pass: {str(e)}")
        # Don't raise the error, as we still want to return the transaction data

    return {"status": "success", "transaction_id": transaction_id}

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
