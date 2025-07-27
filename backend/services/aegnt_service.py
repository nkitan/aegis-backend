
import os
import asyncio
import httpx
from core.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class AegntService:
    def __init__(self):
        """Initialize the agent service with aegnt configuration"""
        try:
            self.aegnt_url = settings.AEGNT_API_URL
            if not self.aegnt_url:
                raise ValueError("AEGNT_API_URL is not configured")
                
            # Initialize httpx client for making requests to aegnt
            self.client = httpx.AsyncClient(base_url=self.aegnt_url)
            
        except Exception as e:
            logger.error(f"Error initializing AegntService: {str(e)}")
            raise

    async def invoke_agent(self, user_id: str, prompt: str, id_token: str):
        """
        Invokes the aegnt with a given prompt.
        
        Args:
            user_id: The ID of the user making the request
            prompt: The prompt to send to the agent
            
        Returns:
            dict: The processed response from the agent
        """
        try:
            logger.info(f"Sending request to aegnt at {self.aegnt_url}")
            
            # Send the message to aegnt
            response = await self.client.post("/invoke_agent", json={
                "user_id": user_id,
                "prompt": prompt,
                "id_token": id_token,
            }, timeout=120.0)  # Add timeout
            
            # Log the response status
            logger.info(f"Received response from aegnt with status {response.status_code}")
            
            # Raise exception for non-200 responses
            response.raise_for_status()
            
            try:
                data = response.json()
                
                # Process response parts from aegnt
                if "parts" in data:
                    processed_parts = []
                    for part in data["parts"]:
                        if part["type"] == "function_call":
                            # Extract function call details
                            processed_parts.append({
                                "type": "function_call",
                                "name": part.get("name"),
                                "args": part.get("args", {}),
                                "content": part.get("content", {})
                            })
                        elif part["type"] == "text":
                            # Process text parts
                            processed_parts.append({
                                "type": "text",
                                "content": part["content"]
                            })
                        else:
                            # Pass through any other part types
                            processed_parts.append(part)
                    
                    return {"parts": processed_parts}
                    
                # Fallback for older response format
                responses = []
                if "content" in data:
                    for part in data["content"].get("parts", []):
                        if "text" in part:
                            responses.append({"type": "text", "content": part["text"]})
                        elif "function_call" in part:
                            responses.append({
                                "type": "function_call",
                                "name": part["function_call"].get("name"),
                                "args": part["function_call"].get("args", {}),
                                "content": part["function_call"]
                            })
                return {"parts": responses}
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding aegnt response: {str(e)}")
                raise ValueError("Invalid response format from aegnt service")
            
        except httpx.HTTPError as e:
            print(e)
            logger.error(f"HTTP error invoking aegnt: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error invoking aegnt: {str(e)}")
            raise
            
    async def __del__(self):
        """Cleanup method to close the HTTP client"""
        if hasattr(self, 'client'):
            await self.client.aclose()
