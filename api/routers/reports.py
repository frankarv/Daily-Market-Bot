from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from bot.agents.market_agent import run_market_agent

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/run", response_class=PlainTextResponse)
def run_report():
    """
    Runs the Claude-powered market analysis agent and returns the Markdown report.
    """
    report = run_market_agent()
    return report
