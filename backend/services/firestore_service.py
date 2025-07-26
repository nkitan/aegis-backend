from google.cloud import firestore
from models.transaction import Transaction
from typing import List
from datetime import datetime

class FirestoreService:
    def __init__(self):
        # The client library will automatically find your credentials if you've set up
        # the GOOGLE_APPLICATION_CREDENTIALS environment variable.
        self.db = firestore.Client()

    def add_transaction(self, user_id: str, transaction_data: dict) -> str:
        """Adds a new transaction to a user's subcollection in Firestore."""
        _, doc_ref = self.db.collection('users', user_id, 'transactions').add(transaction_data)
        return doc_ref.id

    def get_transactions(self, user_id: str, start_date: str, end_date: str, category: str = None, store_name: str = None, item_name: str = None) -> List[Transaction]:
        """Queries transactions for a user based on filters."""
        # Convert string dates to datetime objects
        start_datetime = datetime.fromisoformat(start_date)
        end_datetime = datetime.fromisoformat(end_date)
        
        # Ensure user document exists
        user_ref = self.db.collection('users').document(user_id)
        user_ref.set({}, merge=True)  # Create if not exists
        
        query = self.db.collection('users', user_id, 'transactions')\
            .where('transaction_date', '>=', start_datetime)\
            .where('transaction_date', '<=', end_datetime)

        # Note: When filtering by category, a composite index is required on ['items.category', 'transaction_date']
        if category:
            query = query.where('items.category', '==', category)
        if store_name:
            query = query.where('store_name', '==', store_name)

        results = query.stream()
        transactions = []
        for doc in results:
            data = doc.to_dict()
            if 'id' in data:
                del data['id']  # Remove 'id' if it exists in the document data
            transactions.append(Transaction(id=doc.id, **data))

        if item_name:
            transactions = [t for t in transactions if any(item.name == item_name for item in t.items)]

        return transactions

    def add_challenge(self, user_id: str, challenge_data: dict) -> str:
        """Adds a new challenge to a user's subcollection in Firestore."""
        _, doc_ref = self.db.collection('users', user_id, 'challenges').add(challenge_data)
        return doc_ref.id

    def get_challenges(self, user_id: str) -> List[dict]:
        """Retrieves all challenges for a user."""
        query = self.db.collection('users', user_id, 'challenges').stream()
        return [{**doc.to_dict(), "id": doc.id} for doc in query]

    def update_transaction(self, user_id: str, transaction_id: str, data: dict):
        """Updates an existing transaction in Firestore."""
        self.db.collection('users', user_id, 'transactions').document(transaction_id).update(data)

    def update_user_fcm_token(self, user_id: str, fcm_token: str):
        """Updates a user's FCM token in Firestore."""
        self.db.collection('users').document(user_id).update({'fcm_token': fcm_token})

    def get_user_fcm_token(self, user_id: str) -> str | None:
        """Retrieves a user's FCM token from Firestore."""
        user_doc = self.db.collection('users').document(user_id).get()
        if user_doc.exists:
            return user_doc.to_dict().get('fcm_token')
        return None
