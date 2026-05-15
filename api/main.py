from fastapi import FastAPI

# Import each router explicitly
from api.routers import (
    health,
    reports,
    charts,
    candles,
    candles_intraday,
    candles_multi,
    candles_overlays,
    chart_combined,
    chart_combined_multi,
    chart_commentary,
    chart_commentary_multi,
    portfolio_combined,
    portfolio_commentary,
    portfolio_risk,
    trend_classification,
    trend_strength
)

app = FastAPI(
    title="Market Analysis Agent API",
    description="FastAPI wrapper for the Claude-powered Market Analysis Bot",
    version="1.0.0"
)

# Register routers
app.include_router(health.router)
app.include_router(reports.router)
app.include_router(charts.router)
app.include_router(candles.router)
app.include_router(candles_intraday.router)
app.include_router(candles_multi.router)
app.include_router(candles_overlays.router)
app.include_router(chart_combined.router)
app.include_router(chart_combined_multi.router)
app.include_router(chart_commentary.router)
app.include_router(chart_commentary_multi.router)
app.include_router(portfolio_combined.router)
app.include_router(portfolio_commentary.router)
app.include_router(portfolio_risk.router)
app.include_router(trend_classification.router)
app.include_router(trend_strength.router)
