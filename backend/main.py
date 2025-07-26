
import logging
import time
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from core.config import settings
from routers import users, transactions, integrations, challenges, tasks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url}")
    try:
        response = await call_next(request)
    except Exception as e:
        logger.exception(f"Error processing request: {request.method} {request.url}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
    process_time = time.time() - start_time
    logger.info(f"Response status: {response.status_code} for {request.method} {request.url} in {process_time:.4f} seconds")
    return response

app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(transactions.router, prefix=settings.API_V1_STR, tags=["transactions"])
app.include_router(integrations.router, prefix=settings.API_V1_STR, tags=["integrations"])
app.include_router(challenges.router, prefix=settings.API_V1_STR, tags=["challenges"])
app.include_router(tasks.router, prefix=settings.API_V1_STR, tags=["tasks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Project Aegis Backend"}
