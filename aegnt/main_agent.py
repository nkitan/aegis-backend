"""
Main entry point for the Aegis Agent (Aegnt).

This script defines the main agent, registers the available tools, and starts
the agent's conversational loop. It serves as the primary execution file for
the agent.
"""

from google.adk.agents import Agent
import tool_definitions

# Sub-agent for handling transactions
transaction_agent = Agent(
    name="transaction_agent",
    model="gemini-2.5-flash",
    description="Handles processing and querying of financial transactions.",
    instruction="""You are a specialized agent for handling financial transactions.
    - Use `process_receipt` to process new receipts.
    - Use `query_transactions` to fetch transaction data.
    - Use `get_spending_summary` to provide summaries of spending.""",
    tools=[
        tool_definitions.process_receipt,
        tool_definitions.query_transactions,
        tool_definitions.get_spending_summary,
    ],
)

# Sub-agent for financial planning
planning_agent = Agent(
    name="planning_agent",
    model="gemini-2.5-flash",
    description="Helps users with financial planning, including savings plans and challenges.",
    instruction="""You are a specialized agent for financial planning.
    - Use `generate_savings_plan` to create personalized savings plans.
    - Use `manage_savings_challenge` to manage savings challenges.""",
    tools=[
        tool_definitions.generate_savings_plan,
        tool_definitions.manage_savings_challenge,
    ],
)

# Sub-agent for creative tasks
creative_agent = Agent(
    name="creative_agent",
    model="gemini-2.5-flash",
    description="Provides creative suggestions, such as recipes.",
    instruction="""You are a specialized agent for creative tasks.
    - Use `generate_recipe_suggestion` to suggest recipes based on pantry items.""",
    tools=[tool_definitions.generate_recipe_suggestion],
)

# Sub-agent for notifications and scheduling
notification_agent = Agent(
    name="notification_agent",
    model="gemini-2.5-flash",
    description="Manages notifications and calendar events.",
    instruction="""You are a specialized agent for sending notifications and creating calendar events.
    - Use `send_push_notification` to send alerts to the user.
    - Use `create_calendar_event` to schedule events.""",
    tools=[
        tool_definitions.send_push_notification,
        tool_definitions.create_calendar_event,
    ],
)

# Sub-agent for proactive analysis
proactive_agent = Agent(
    name="proactive_agent",
    model="gemini-2.5-flash",
    description="Performs proactive analysis of user's financial data.",
    instruction="""You are a specialized agent for proactive financial analysis.
    - Use `run_proactive_analysis` to find trends and insights in user's spending.""",
    tools=[tool_definitions.run_proactive_analysis],
)

# Sub-agent for Google Wallet
wallet_agent = Agent(
    name="wallet_agent",
    model="gemini-2.5-flash",
    description="Manages Google Wallet passes.",
    instruction="""You are a specialized agent for managing Google Wallet passes.
    - Use `create_wallet_pass` to create new wallet passes.""",
    tools=[tool_definitions.create_wallet_pass],
)


# The main agent
root_agent = Agent(
    name="Aegnt",
    global_instruction="""You are Aegnt, a sophisticated AI financial assistant.
    Your primary role is to orchestrate a suite of tools by delegating tasks to specialized sub-agents.
    You interact with the user, understand their needs, and then route the request to the correct sub-agent.
    After a sub-agent completes a task, you present the result to the user and ask if there is anything else you can help with.""",
    instruction="""You are the main financial assistant.
    - Greet the user and ask how you can help.
    - Based on the user's request, delegate the task to the appropriate sub-agent.
    - For transaction-related queries, use the `transaction_agent`.
    - For financial planning, use the `planning_agent`.
    - For creative requests like recipes, use the `creative_agent`.
    - For notifications and calendar events, use the `notification_agent`.
    - For proactive analysis, use the `proactive_agent`.
    - For Google Wallet integration, use the `wallet_agent`.
    - When the conversation is over, say goodbye politely.""",
    sub_agents=[
        transaction_agent,
        planning_agent,
        creative_agent,
        notification_agent,
        proactive_agent,
        wallet_agent,
    ],
    model="gemini-2.5-flash",
)

from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent

import asyncio

async def main():
    print("Aegnt is running. You can now interact with it.")
    print("Type 'exit' to end the conversation.")

    runner = InMemoryRunner(agent=root_agent)
    session = await runner.session_service.create_session(app_name=runner.app_name, user_id="user")
    print(f"Created session for user ID: user")

    while True:
        user_input = input("User: ")
        if user_input.lower() == 'exit':
            break

        content = UserContent(parts=[Part(text=user_input)])
        response_text = ""
        async for event in runner.run_async(
            user_id=session.user_id, session_id=session.id, new_message=content
        ):
            if event.content and event.content.parts and event.content.parts[0].text:
                response_text += event.content.parts[0].text
        print(f"Agent: {response_text}")

    await runner.session_service.delete_session(user_id=session.user_id, session_id=session.id)
    print(f"Deleted session for user ID: user")

if __name__ == "__main__":
    asyncio.run(main())
