from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from bot.agents.market_agent import run_market_agent

app = FastAPI(
    title="Market Analysis Agent API",
    description="FastAPI wrapper for the Claude-powered Market Analysis Bot",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Market Analysis Agent API is running"}

@app.get("/run-report", response_class=PlainTextResponse)
def run_report():
    """
    Runs the Claude-powered market analysis agent and returns the Markdown report.
    """
    report = run_market_agent()
    return report
