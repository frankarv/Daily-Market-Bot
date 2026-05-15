from fastapi import FastAPI
from api.routers import reports, health

app = FastAPI(
    title="Market Analysis Agent API",
    description="FastAPI wrapper for the Claude-powered Market Analysis Bot",
    version="1.0.0"
)

# Routers
app.include_router(health.router)
app.include_router(reports.router)
