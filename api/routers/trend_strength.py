import yfinance as yf
import numpy as np
import pandas as pd
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import os
from anthropic import Anthropic

router = APIRouter(prefix="/charts", tags=["Trend Strength"])

client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

@router.get("/trend-strength")
def trend_strength_score(
    symbol: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    days: int = Query(90, description="Number of days of history to analyze")
):
    """
    Returns a 0–100 trend strength score plus AI-generated interpretation.
    """
    data = yf.download(symbol, period=f"{days}d", interval="1d")

    if data.empty:
        return {"error": f"No data found for symbol {symbol}"}

    close = data["Close"]

    # --- Trend slope ---
    x = np.arange(len(close))
    slope, _ = np.polyfit(x, close.values, 1)

    # --- Moving averages ---
    sma20 = close.rolling(20).mean().iloc[-1]
    sma50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else None

    # --- RSI ---
    rsi = compute_rsi(close).iloc[-1]

    # --- Volatility ---
    volatility = float(close.pct_change().std() * 100)

    # --- Trend Strength Score (0–100) ---
    score = 0

    # Slope contribution
    score += np.tanh(slope / close.iloc[-1] * 50) * 20

    # SMA alignment
    if sma50:
        if sma20 > sma50:
            score += 20
        else:
            score -= 20

    # RSI contribution
    if rsi > 70:
        score -= 10
    elif rsi < 30:
        score += 10
    else:
        score += (rsi - 50) / 5  # mild contribution

    # Volatility penalty
    if volatility > 3:
        score -= min(15, (volatility - 3) * 2)

    # Normalize to 0–100
    score = max(0, min(100, 50 + score))

    # --- Summary for AI ---
    summary = (
        f"Trend strength analysis for {symbol} ({days} days):\n"
        f"- Slope: {slope:.4f}\n"
        f"- SMA20: {sma20:.2f}\n"
        f"- SMA50: {sma50:.2f if sma50 else 'N/A'}\n"
        f"- RSI: {rsi:.2f}\n"
        f"- Volatility: {volatility:.2f}%\n"
        f"- Trend Strength Score (0–100): {score:.1f}\n"
    )

    # --- AI Interpretation ---
    prompt = (
        "You are a financial analyst. Interpret the following trend strength metrics "
        "in a concise, non-speculative way:\n\n"
        f"{summary}\n"
        "Focus on:\n"
        "- Trend direction and momentum\n"
        "- Strength vs weakness\n"
        "- Volatility regime\n"
        "- Whether indicators agree or conflict\n"
        "- What stands out\n\n"
        "Do NOT give financial advice or predictions."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )

    commentary = response.content[0].text

    return JSONResponse({
        "symbol": symbol.upper(),
        "days_analyzed": days,
        "trend_strength_score": score,
        "metrics": {
            "slope": slope,
            "sma20": sma20,
            "sma50": sma50,
            "rsi": rsi,
            "volatility_pct": volatility
        },
        "summary": summary,
        "commentary": commentary
    })
