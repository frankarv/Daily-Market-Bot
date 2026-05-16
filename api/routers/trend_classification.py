import yfinance as yf
import numpy as np
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import os
from anthropic import Anthropic

router = APIRouter(prefix="/charts", tags=["Trend Classification"])

client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))

@router.get("/trend")
def classify_trend(
    symbol: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    days: int = Query(60, description="Number of days of history to analyze")
):
    """
    Returns a trend classification (uptrend, downtrend, sideways)
    plus AI-generated interpretation.
    """
    data = yf.download(symbol, period=f"{days}d", interval="1d")

    if data.empty:
        return {"error": f"No data found for symbol {symbol}"}

    close = data["Close"]

    # --- Compute trend slope ---
    x = np.arange(len(close))
    slope, intercept = np.polyfit(x, close.values, 1)

    # --- Compute moving averages ---
    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None

    # --- Compute volatility ---
    volatility = float(close.pct_change().std() * 100)

    # --- Trend classification rules ---
    if slope > 0 and (sma50 is None or sma20 > sma50):
        trend = "Uptrend"
    elif slope < 0 and (sma50 is None or sma20 < sma50):
        trend = "Downtrend"
    else:
        trend = "Sideways / Consolidation"

    # --- Summary for AI ---
    summary = (
        f"{symbol} trend summary ({days} days):\n"
        f"- Trend slope: {slope:.4f}\n"
        f"- SMA20: {sma20:.2f}\n"
        f"- SMA50: {sma50:.2f if sma50 else 'N/A'}\n"
        f"- Volatility: {volatility:.2f}%\n"
        f"- Classified trend: {trend}\n"
    )

    # --- AI Interpretation ---
    prompt = (
        "You are a financial analyst. Interpret the following trend data "
        "in a concise, non-speculative way:\n\n"
        f"{summary}\n"
        "Focus on:\n"
        "- Trend direction\n"
        "- Momentum\n"
        "- Volatility regime\n"
        "- Whether the trend is strengthening or weakening\n"
        "- What stands out\n\n"
        "Do NOT give financial advice or predictions."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    commentary = response.content[0].text

    return JSONResponse({
        "symbol": symbol.upper(),
        "days_analyzed": days,
        "trend": trend,
        "slope": slope,
        "sma20": sma20,
        "sma50": sma50,
        "volatility_pct": volatility,
        "summary": summary,
        "commentary": commentary
    })
