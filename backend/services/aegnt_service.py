
import httpx
from core.config import settings

class AegntService:
    def __init__(self):
        self.base_url = settings.AEGNT_API_URL

    def invoke_agent(self, user_id: str, prompt: str):
        """
        Invokes the Aegnt agent with a given prompt.
        """
        with httpx.Client() as client:
            response = client.post(
                f"{self.base_url}/invoke_agent",
                json={"user_id": user_id, "prompt": prompt},
                timeout=120,  # Set a longer timeout (in seconds)
            )
            response.raise_for_status()
            return response.json()
