
from core.config import settings
import json
from datetime import datetime, timezone
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth import jwt, crypt
import logging

logger = logging.getLogger(__name__)

class GoogleWalletService:
    def __init__(self):
        """Initialize the Google Wallet service with service account credentials."""
        try:
            self.credentials = Credentials.from_service_account_file(
                settings.GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE,
                scopes=['https://www.googleapis.com/auth/wallet_object.issuer']
            )
            self.client = build('walletobjects', 'v1', credentials=self.credentials)
        except Exception as e:
            logger.error(f"Error initializing Google Wallet service: {str(e)}")
            raise

    def create_pass(self, pass_type: str, pass_data: dict) -> str:
        """
        Creates a Google Wallet pass for the given type and data.
        
        Args:
            pass_type: The type of pass to create (e.g., 'transaction', 'loyalty', etc.)
            pass_data: The data to include in the pass
            
        Returns:
            str: The "Add to Google Wallet" URL
            
        Raises:
            ValueError: If required data is missing
            Exception: If there's an error creating the pass
        """
        try:
            issuer_id = settings.GOOGLE_WALLET_ISSUER_ID
            if not issuer_id:
                raise ValueError("GOOGLE_WALLET_ISSUER_ID is not configured")

            class_suffix = f"{pass_type}_class"
            object_suffix = pass_data.get("transaction_id")
            if not object_suffix:
                raise ValueError("transaction_id is required in pass_data")

            # Define the Generic Class with minimal required fields
            generic_class = {
                "id": f"{issuer_id}.{class_suffix}",
                "classTemplateInfo": {
                    "cardTemplateOverride": {
                        "cardRowTemplateInfo": {
                            "twoItems": {
                                "startItem": {
                                    "firstValue": {
                                        "fields": [{"fieldPath": "object.textModulesData['store']"}]
                                    }
                                },
                                "endItem": {
                                    "firstValue": {
                                        "fields": [{"fieldPath": "object.textModulesData['totalAmount']"}]
                                    }
                                }
                            }
                        }
                    }
                },
                "reviewStatus": "UNDER_REVIEW"  # Required for updates
            }

            # No need to explicitly create the class - it will be created when the user adds the pass

            # Define the Generic Object with required fields
            generic_object = {
                "id": f"{issuer_id}.{object_suffix}",
                "classId": f"{issuer_id}.{class_suffix}",
                "state": "ACTIVE",
                "cardTitle": {
                    "defaultValue": {
                        "language": "en",
                        "value": f"{pass_data.get('store_name', 'Transaction')} Receipt"
                    }
                },
                "header": {
                    "defaultValue": {
                        "language": "en",
                        "value": f"${pass_data.get('total_amount', 0.0):.2f}"
                    }
                },
                "barcode": {
                    "type": "QR_CODE",
                    "value": json.dumps(pass_data),
                    "alternateText": f"Transaction ID: {pass_data['transaction_id']}"
                },
                "textModulesData": [
                    {"header": "Store", "body": pass_data.get("store_name", "N/A"), "id": "store"},
                    {"header": "Total Amount", "body": f"${pass_data.get('total_amount', 0.0):.2f}", "id": "totalAmount"},
                    {"header": "Date", "body": pass_data.get("transaction_date", "N/A"), "id": "date"},
                    {"header": "Category", "body": pass_data.get("category", "N/A"), "id": "category"},
                    {"header": "Items", "body": ", ".join([i.get('name', 'Unknown') for i in pass_data.get("items", [])]), "id": "items"}
                ],
                "hexBackgroundColor": "#4285f4",
                "logo": {
                    "sourceUri": {
                        "uri": "https://storage.googleapis.com/wallet-lab-tools-codelab-artifacts-public/pass_google_logo.jpg"
                    },
                    "contentDescription": {
                        "defaultValue": {
                            "language": "en",
                            "value": "Aegis Logo"
                        }
                    }
                }
            }

            # Add optional location if available
            if store_location := pass_data.get("store_location"):
                location_data = {
                    "address": store_location.get("address", ""),
                    "city": store_location.get("city", ""),
                    "state": store_location.get("state", ""),
                    "postalCode": store_location.get("postal_code", ""),
                    "country": store_location.get("country", "")
                }
                if all(location_data.values()):  # Only add if we have all location fields
                    generic_object["locations"] = [{"kind": "walletobjects#latLongPoint", **location_data}]

            # Create JWT claims with both class and object definitions
            claims = {
                "iss": self.credentials.service_account_email,
                "aud": "google",
                "origins": ["https://127.0.0.1:8000"],
                "typ": "savetowallet",
                "payload": {
                    "genericClasses": [generic_class],
                    "genericObjects": [generic_object]
                },
                "iat": int(datetime.now(timezone.utc).timestamp()),
                "exp": int(datetime.now(timezone.utc).timestamp() + 3600)  # Token expires in 1 hour
            }

            signer = crypt.RSASigner.from_service_account_file(settings.GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE)
            token = jwt.encode(signer, claims)
            return f"https://pay.google.com/gp/v/save/{token}"
        except Exception as e:
            logger.error(f"Error creating Google Wallet pass: {str(e)}")
            raise
