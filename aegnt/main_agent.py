"""
Main entry point for the Aegis Agent (Aegnt).

This script defines the main agent, registers the available tools, and starts
the agent's conversational loop. It serves as the primary execution file for
the agent.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
import tool_definitions
from google.adk.runners import InMemoryRunner
from google.genai.types import Part, UserContent
import asyncio

# Sub-agent for handling transactions
transaction_agent = Agent(
    name="transaction_agent",
    model="gemini-2.5-flash",
    description="Handles processing and querying of financial transactions.",
    instruction="""You are a specialized agent for handling financial transactions.
    - For all data retrieval, you MUST use `query_transactions` to fetch transaction data based on user's query, including date ranges, categories, and store names. DO NOT use any external search tools.
    - Use `process_receipt` to process new receipts.
    - After fetching transactions with `query_transactions`, use `summarize_transactions` to provide summaries of spending and insights from the retrieved data.
    - Crucially, you must NEVER ask the user for their user ID or ID token, as these are automatically provided to the tools.""",
    tools=[
        tool_definitions.process_receipt,
        tool_definitions.query_transactions,
        tool_definitions.summarize_transactions,
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
    - Use `run_proactive_analysis` to find trends and insights in user's spending.
    **NEVER ask the user for their user ID or ID token.**""",
    tools=[tool_definitions.run_proactive_analysis],
)

# Sub-agent for Google Wallet
wallet_agent = Agent(
    name="wallet_agent",
    model="gemini-2.5-flash",
    description="Manages Google Wallet passes.",
    instruction="""You are a specialized agent for managing Google Wallet passes. The user_id is automatically provided by the system and should not be requested from the user.
    - Use `create_wallet_pass` to create new wallet passes.""",
    tools=[tool_definitions.create_wallet_pass],
)


# The main agent
root_agent = Agent(
    name="Aegnt",
    model="gemini-2.5-flash",
    global_instruction="""You are Aegnt, a sophisticated AI financial assistant.
    Your primary role is to orchestrate a suite of tools by delegating tasks to specialized sub-agents.
    You interact with the user, understand their needs, and then route the request to the correct sub-agent.
    NEVER ask the user for their user ID or ID token, as these are automatically provided by the system to the tools.
    When encountering a financial query or request:
    - For transaction-related queries, use the transaction_agent
    - For financial planning, use the planning_agent
    - For recipe suggestions, use the creative_agent
    - For notifications and scheduling, use the notification_agent
    - For proactive insights, use the proactive_agent
    - For wallet pass creation, use the wallet_agent
    
    Make sure to properly format your responses and handle both text and function calls appropriately.
    After a sub-agent completes a task, present the result to the user and ask if there is anything else you can help with.""",
    instruction="""You are the main financial assistant.
    - Greet the user and ask how you can help.
    - Based on the user's request, delegate the task to the appropriate sub-agent.
    - For transaction-related queries, use the `transaction_agent`.
    - For financial planning, use the `planning_agent`.
    - For creative requests like recipes, use the `creative_agent`.
    - For notifications and calendar events, use the `notification_agent`.
    - For proactive analysis, use the `proactive_agent`.
    - For Google Wallet integration, use the `wallet_agent`.
    - Crucially, you must NEVER ask the user for their user ID, as it is automatically provided to the tools.
    - When the conversation is over, say goodbye politely.""",
    tools=[
        AgentTool(agent=transaction_agent),
        AgentTool(agent=planning_agent),
        AgentTool(agent=creative_agent),
        AgentTool(agent=notification_agent),
        AgentTool(agent=proactive_agent),
        AgentTool(agent=wallet_agent),
    ],
)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request validation middleware
@app.middleware("http")
async def validate_request(request: Request, call_next):
    if request.method == "POST" and not request.headers.get("content-type") == "application/json":
        return JSONResponse(
            status_code=400,
            content={"detail": "Content-Type must be application/json"}
        )
    response = await call_next(request)
    return response

runner = InMemoryRunner(agent=root_agent)

class AegntRequest(BaseModel):
    user_id: str
    prompt: str
    id_token: str

@app.post("/invoke_agent")
async def invoke_agent(request: AegntRequest):
    print(f"Received request from user: {request.user_id}")
    if not request.prompt or not request.prompt.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Empty prompt received"}
        )
    
    session = None
    try:
        # Create a new session
        session = await runner.session_service.create_session(app_name=runner.app_name, user_id=request.user_id)
        content = UserContent(parts=[Part(text=request.prompt)])
        response_parts = []
        async for event in runner.run_async(
            user_id=request.user_id, session_id=session.id, new_message=content
        ):
            if event.content and event.content.parts:
                # Check if we have function calls
                has_function_calls = any(
                    part.function_call for part in event.content.parts
                )
                
                for part in event.content.parts:
                    if has_function_calls and part.function_call:
                        # Handle function calls
                        tool_args = part.function_call.args
                        tool_args['user_id'] = request.user_id
                        tool_args['id_token'] = request.id_token
                        part_data = {
                            "type": "function_call",
                            "name": part.function_call.name,
                            "args": tool_args,
                            "content": part.function_call.model_dump()
                        }
                        response_parts.append(part_data)
                    elif part.text:
                        # Handle text parts
                        part_data = {
                            "type": "text",
                            "content": part.text
                        }
                        response_parts.append(part_data)
                    else:
                        # Handle any other part types
                        part_data = {
                            "type": "other",
                            "content": part.model_dump(exclude_none=True)
                        }
                        response_parts.append(part_data)

        await runner.session_service.delete_session(
            user_id=request.user_id,
            session_id=session.id,
            app_name=runner.app_name
        )
        
        if not response_parts:
            return {"response": "No response from agent."}
            
        return {"parts": response_parts}
    except Exception as e:
        print(f"Error in invoke_agent: {e}")
        if session:
            try:
                await runner.session_service.delete_session(
                    user_id=session.user_id,
                    session_id=session.id,
                    app_name=runner.app_name
                )
            except Exception as cleanup_error:
                print(f"Error cleaning up session: {cleanup_error}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001,
        log_level="info",
        access_log=True,
        timeout_keep_alive=65,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stderr",
                }
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO"},
                "uvicorn.error": {"level": "INFO"},
                "uvicorn.access": {"handlers": ["default"], "level": "INFO", "propagate": False},
            },
        }
    )