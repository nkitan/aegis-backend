
from core.config import settings
import json
import google.auth
import googleapiclient.discovery
from google.auth import jwt, crypt

class GoogleWalletService:
    def __init__(self):
        credentials, project_id = google.auth.load_credentials_from_file(
            settings.GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE,
            scopes=["https://www.googleapis.com/auth/walletobjects"]
        )
        self.wallet_service = googleapiclient.discovery.build(
            "walletobjects", "v1", credentials=credentials
        )

    def create_pass(self, pass_data: dict) -> str:
        issuer_id = settings.GOOGLE_WALLET_ISSUER_ID
        class_suffix = "transaction_class"
        object_suffix = pass_data["transaction_id"]

        # Define the Generic Class
        generic_class = {
            "id": f"{issuer_id}.{class_suffix}",
            "classTemplateInfo": {
                "cardTemplateOverride": {
                    "cardRowTemplateInfo": {
                        "twoItems": {
                            "startItem": {
                                "fieldSelector": {
                                    "fields": [
                                        {"fieldPath": "textModulesData['store']"}
                                    ]
                                }
                            },
                            "endItem": {
                                "fieldSelector": {
                                    "fields": [
                                        {"fieldPath": "textModulesData['totalAmount']"}
                                    ]
                                }
                            }
                        }
                    }
                }
            },
            "textModulesData": [
                {"header": "Store", "body": "N/A", "id": "store"},
                {"header": "Total Amount", "body": "N/A", "id": "totalAmount"},
                {"header": "Date", "body": "N/A", "id": "date"},
                {"header": "Category", "body": "N/A", "id": "category"},
                {"header": "Items", "body": "N/A", "id": "items"},
            ],
            "reviewStatus": "UNDER_REVIEW",
            "multipleObjectsCreateMode": "MULTIPLE_OBJECTS_CREATE_MODE_UNSPECIFIED",
        }

        # Try to get the class, if it doesn't exist, create it
        try:
            self.wallet_service.genericclass().get(resourceId=f"{issuer_id}.{class_suffix}").execute()
        except googleapiclient.errors.HttpError as e:
            if e.resp.status == 404:
                self.wallet_service.genericclass().insert(body=generic_class).execute()
            else:
                raise

        # Define the Generic Object
        generic_object = {
            "id": f"{issuer_id}.{object_suffix}",
            "classId": f"{issuer_id}.{class_suffix}",
            "state": "ACTIVE",
            "barcode": {
                "type": "QR_CODE",
                "value": json.dumps(pass_data),
                "alternateText": f"Transaction ID: {pass_data['transaction_id']}",
            },
            "textModulesData": [
                {"header": "Store", "body": pass_data.get("store_name", "N/A"), "id": "store"},
                {"header": "Total Amount", "body": f"${pass_data.get('total_amount', 0.0):.2f}", "id": "totalAmount"},
                {"header": "Date", "body": pass_data.get("transaction_date", "N/A"), "id": "date"},
                {"header": "Category", "body": pass_data.get("category", "N/A"), "id": "category"},
                {"header": "Items", "body": ", ".join(pass_data.get("items", [])), "id": "items"},
            ],
            "linksModuleData": {
                "uris": [
                    {
                        "uri": "https://localhost:8000/transaction_details",
                        "description": "View transaction details",
                        "id": "transactionDetails",
                    }
                ]
            },
        }

        # Create the Generic Object
        self.wallet_service.genericobject().insert(body=generic_object).execute()

        # Generate the "Add to Google Wallet" URL
        jwt_payload = {
            "aud": "google",
            "iss": "google.com",
            "iat": google.auth.datetime.datetime.utcnow().timestamp(),
            "typ": "savetowallet",
            "origins": [],
            "payload": {"genericObjects": [generic_object]},
        }

        # The GoogleWalletPassGenerator library handles JWT signing.
        # Since we are using the raw API, we need to sign the JWT manually.
        # This requires the private key from the service account file.
        # For simplicity, I'll assume the GoogleWalletPassGenerator library
        # has a utility for this or we'll need to implement it.
        # For now, I'll use a placeholder for the JWT.
        # In a real application, you would use a library like `PyJWT` to sign this.

        signer = crypt.RSASigner.from_service_account_file(settings.GOOGLE_WALLET_SERVICE_ACCOUNT_KEY_FILE)
        token = jwt.encode(signer, jwt_payload).decode('utf-8')
        return f"https://pay.google.com/gp/v/save/{token}"
