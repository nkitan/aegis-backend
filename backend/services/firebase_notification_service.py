
from firebase_admin import messaging
from services.firestore_service import FirestoreService

class FirebaseNotificationService:
    def __init__(self):
        self.firestore_service = FirestoreService()

    def send_notification(self, user_id: str, message: str):
        """
        Sends a push notification to a user's device.
        """
        registration_token = self.firestore_service.get_user_fcm_token(user_id)

        if not registration_token:
            print(f"No FCM token found for user {user_id}. Notification not sent.")
            return

        message = messaging.Message(
            notification=messaging.Notification(
                title='Aegis Notification',
                body=message,
            ),
            token=registration_token,
        )

        try:
            response = messaging.send(message)
            print('Successfully sent message:', response)
        except Exception as e:
            print('Error sending message:', e)
