
import httpx
from core.config import settings

class AegntService:
    def __init__(self):
        # You'll need to add AEGN_API_URL to your settings
        self.base_url = settings.AEGNT_API_URL

    def trigger_proactive_analysis(self, user_id: str):
        """
        Triggers the proactive analysis tool in the Aegnt agent.
        """
        with httpx.Client() as client:
            response = client.post(f"{self.base_url}/run_proactive_analysis", json={"user_id": user_id})
            response.raise_for_status()
            return response.json()
