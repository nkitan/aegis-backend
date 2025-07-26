import pytest
import os
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from aegnt.main_agent import root_agent

pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session", autouse=True)
def load_env():
    load_dotenv()

@pytest.mark.asyncio
async def test_transaction_query():
    """Tests the transaction query functionality."""
    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(
        app_name=runner.app_name, user_id="test_user_transactions"
    )

    user_input = "How much did I spend on groceries last month?"

    content = UserContent(parts=[Part(text=user_input)])
    response_text = ""
    function_calls = []

    async for event in runner.run_async(
        user_id=session.user_id,
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text
                elif part.function_call:
                    function_calls.append({
                        'name': part.function_call.model_dump().get('name'),
                        'args': part.function_call.model_dump().get('args', {})
                    })
                    
    # Verify that transaction_agent was called with the correct query
    assert len(function_calls) > 0, "No function calls were made"
    assert any(
        call['name'] == 'transaction_agent' and 
        'request' in call['args'] and
        'groceries' in call['args']['request'].lower()
        for call in function_calls
    ), "Expected transaction_agent call for groceries query not found"
