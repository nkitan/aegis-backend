"""
Main entry point for the Aegis Financial Agent (Aegnt).

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
    description="Handles processing and querying of financial transactions with analysis.",
    instruction="""You are a specialized agent for handling financial transactions and analysis.
    
    CRITICAL INSTRUCTIONS:
    - ALWAYS use `analyze_financial_data` for ANY financial questions about spending, transactions, or money
    - This function is SMART and will automatically determine appropriate date ranges and categories based on the user's question
    - DO NOT manually specify date ranges unless the user explicitly mentions specific dates
    - For broad queries like "spending trends", "what store did I spend the most at", "total spending", the function will automatically use a wide date range to find all relevant data
    - For time-specific queries like "last month" or "2017", the function will automatically set the correct date range
    - For category queries like "restaurant spending", the function will automatically detect and filter by category
    - The function retrieves REAL data from the user's database and provides AI analysis in one step
    - NEVER make up numbers or provide generic responses
    - Present the analysis results clearly, mentioning specific amounts, dates, and stores from the real data
    - If no data is found, explain that clearly rather than making up answers
    - Use `process_receipt` only for processing new receipts
    - You must NEVER ask the user for their user ID or ID token, as these are automatically provided to the tools.""",
    tools=[
        tool_definitions.process_receipt,
        tool_definitions.analyze_financial_data,
    ],
)

# Sub-agent for financial planning
planning_agent = Agent(
    name="planning_agent",
    model="gemini-2.5-flash",
    description="Helps users with financial planning, including savings plans and challenges.",
    instruction="""You are a specialized agent for financial planning.
    - Use `generate_savings_plan` to create personalized savings plans.
    - Use `manage_savings_challenge` to manage savings challenges.
    - Use `analyze_financial_data` if you need to analyze spending patterns for planning purposes.""",
    tools=[
        tool_definitions.generate_savings_plan,
        tool_definitions.manage_savings_challenge,
        tool_definitions.analyze_financial_data,
    ],
)

# Sub-agent for creative tasks
creative_agent = Agent(
    name="creative_agent",
    model="gemini-2.5-flash",
    description="Provides creative suggestions, such as recipes based on virtual pantry items from recent purchases.",
    instruction="""You are a specialized agent for creative tasks.
    - Use `generate_recipe_suggestion` to suggest recipes based on ingredients automatically detected from the user's recent grocery purchases.
    - The system will automatically extract pantry items from recent receipts, so you don't need to ask the user what ingredients they have.
    - NEVER ask the user for their user ID or ID token, as these are automatically provided to the tools.""",
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
    description="Performs proactive analysis of user's financial data to provide insights.",
    instruction="""You are a specialized agent for proactive financial analysis and insights.
    
    When the user asks for proactive insights about their financial health:
    
    1. Start by saying "Let me analyze your recent financial activity..."
    2. FIRST try using `run_proactive_analysis` to get automated insights
    3. If that doesn't provide insights, use `analyze_financial_data` with a query like "Show me my recent spending patterns and trends" to get transaction data and provide your own analysis
    4. If no transaction data is available, use `get_basic_financial_insight` to provide helpful financial tips
    5. Always provide helpful insights and actionable recommendations
    
    Your responses should be:
    - Friendly and conversational
    - Based on actual data when available, or helpful tips when not
    - Include specific recommendations
    - Encouraging and helpful
    - Always provide value to the user
    
    **ALWAYS provide some form of helpful insight, even if transaction data is unavailable.**
    **NEVER say you cannot access financial data without trying the available tools first.**
    **NEVER ask the user for their user ID or ID token - these are automatically provided.**
    
    Your goal is to be proactive and helpful with financial insights.""",
    tools=[
        tool_definitions.analyze_financial_data,
        tool_definitions.run_proactive_analysis,
        tool_definitions.run_comprehensive_proactive_analysis,
        tool_definitions.schedule_proactive_insights,
        tool_definitions.get_user_insights_history,
        tool_definitions.get_basic_financial_insight
    ],
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
    Your primary role is to help users with financial analysis by using the available tools.
    
    CRITICAL ROUTING RULES:
    
    1. For PROACTIVE INSIGHTS (keywords: "proactive insight", "random insight", "financial health insight", "spending insight"):
       - Delegate to proactive_agent
       - Do NOT use analyze_financial_data for these requests
    
    2. For SPECIFIC FINANCIAL QUERIES (with specific questions about amounts, dates, stores):
       - Use analyze_financial_data tool DIRECTLY
       - Examples: "How much did I spend?", "What store?", "Show me trends", "Total spending"
    
    3. For OTHER TASKS:
       - Receipt processing: use transaction_agent
       - Financial planning: use planning_agent  
       - Recipe suggestions: use creative_agent
       - Notifications and calendar: use notification_agent
       - Wallet passes: use wallet_agent
    
    The analyze_financial_data tool is smart and will:
    - Automatically determine appropriate date ranges based on the user's question
    - Detect categories from natural language (restaurant, grocery, etc.)
    - Retrieve real data from the database
    - Provide AI-powered analysis
    
    Examples of queries to handle with analyze_financial_data:
    - "How much did I spend on restaurant food last month?"
    - "What was my total spending in 2017?"
    - "Show me my spending trends by category"
    - "What store did I spend the most at?"
    - "How much did I spend on groceries?"
    
    Examples of queries to delegate to proactive_agent:
    - "Give me a proactive insight about my financial health"
    - "Give me a random insight"
    - "Provide a proactive insight about my spending patterns"
    - "Get proactive insight"
    
    NEVER ask the user for their user ID or ID token, as these are automatically provided.""",
    instruction="""You are the main financial assistant.
    - Greet the user and ask how you can help.
    - For PROACTIVE INSIGHTS, delegate to proactive_agent.
    - For SPECIFIC financial analysis queries, use the `analyze_financial_data` tool directly.
    - For other tasks, delegate to the appropriate sub-agent.
    - Crucially, you must NEVER ask the user for their user ID, as it is automatically provided to the tools.
    - When the conversation is over, say goodbye politely.""",
    tools=[
        tool_definitions.analyze_financial_data,
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