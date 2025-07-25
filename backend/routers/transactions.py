
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
    transaction_data = {
        "user_id": current_user.uid,
        "transaction_date": datetime.fromisoformat(receipt_data["transaction_date"]) if "transaction_date" in receipt_data else datetime.now(),
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
    wallet_pass_data = {
        "transaction_id": transaction_id,
        "store_name": transaction_data.get("store_name"),
        "total_amount": transaction_data.get("total_amount"),
        "transaction_date": transaction_data.get("transaction_date").isoformat(),
        "category": transaction_data.get("category")
    }
    google_wallet_service.create_pass("transaction", wallet_pass_data)

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
