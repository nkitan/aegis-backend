import textwrap
import pytest
import asyncio
import os
from dotenv import load_dotenv

from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

# Import the root_agent from your main_agent.py
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main_agent import root_agent

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()

@pytest.mark.asyncio
async def test_recipe_suggestion():
    """Tests the recipe suggestion functionality using Spoonacular API."""
    # Ensure SPOONACULAR_API_KEY is set for this test to run successfully
    if not os.getenv("SPOONACULAR_API_KEY"):
        pytest.skip("SPOONACULAR_API_KEY not set. Skipping recipe test.")

    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user_recipe"
    )

    user_input = textwrap.dedent(
        """
        Suggest a recipe using chicken, rice, and broccoli.
        """
    ).strip()

    content = UserContent(parts=[Part(text=user_input)])
    response_text = ""
    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if hasattr(part, 'text') and part.text:
                    response_text += part.text
                elif hasattr(part, 'function_call'):
                    # Handle function calls by recording them or processing them as needed
                    function_call = part.function_call
                    print(f"Function called: {function_call.name} with args: {function_call.args}")
            response_text += event.content.parts[0].text

    # Assertions to check if the recipe suggestion is as expected
    # This will depend on the actual output format from Spoonacular and your agent's processing
    assert "Recipe:" in response_text
    assert "chicken" in response_text.lower()
    assert "rice" in response_text.lower()
    assert "broccoli" in response_text.lower()
    assert "Used Ingredients:" in response_text

    await runner.session_service.delete_session(user_id=session.user_id, session_id=session.id)
