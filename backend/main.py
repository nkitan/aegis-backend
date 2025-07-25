
from fastapi import FastAPI
from core.config import settings
from routers import users, transactions, integrations, challenges, tasks

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(users.router, prefix=settings.API_V1_STR, tags=["users"])
app.include_router(transactions.router, prefix=settings.API_V1_STR, tags=["transactions"])
app.include_router(integrations.router, prefix=settings.API_V1_STR, tags=["integrations"])
app.include_router(challenges.router, prefix=settings.API_V1_STR, tags=["challenges"])
app.include_router(tasks.router, prefix=settings.API_V1_STR, tags=["tasks"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Project Aegis Backend"}
