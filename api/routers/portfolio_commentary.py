import yfinance as yf
import pandas as pd
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import os
from anthropic import Anthropic

router = APIRouter(prefix="/portfolio", tags=["AI Portfolio Commentary"])

client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))

@router.get("/commentary")
def portfolio_commentary(
    symbols: str = Query(..., description="Comma-separated tickers, e.g. AAPL,MSFT,GOOG"),
    weights: str = Query(..., description="Comma-separated weights (must sum to 1.0), e.g. 0.4,0.3,0.3"),
    days: int = Query(60, description="Number of days of history to analyze")
):
    """
    Returns AI-generated commentary on a weighted portfolio of assets.
    """
    tickers = [s.strip().upper() for s in symbols.split(",")]
    weight_list = [float(w.strip()) for w in weights.split(",")]

    if len(tickers) != len(weight_list):
        return {"error": "Number of symbols must match number of weights"}

    if abs(sum(weight_list) - 1.0) > 0.001:
        return {"error": "Weights must sum to 1.0"}

    # Download data
    data = yf.download(tickers, period=f"{days}d", interval="1d")["Close"]

    if data.empty:
        return {"error": "No data found for the provided symbols"}

    # Compute portfolio value series
    normalized = data / data.iloc[0]
    portfolio_series = (normalized * weight_list).sum(axis=1)

    # Portfolio stats
    first = float(portfolio_series.iloc[0])
    latest = float(portfolio_series.iloc[-1])
    pct_change = ((latest - first) / first) * 100
    high = float(portfolio_series.max())
    low = float(portfolio_series.min())
    volatility = float(portfolio_series.pct_change().std() * 100)

    portfolio_summary = (
        f"Portfolio summary ({days} days):\n"
        f"- Symbols: {tickers}\n"
        f"- Weights: {weight_list}\n"
        f"- First value: {first:.4f}\n"
        f"- Latest value: {latest:.4f}\n"
        f"- High: {high:.4f}\n"
        f"- Low: {low:.4f}\n"
        f"- % Change: {pct_change:.2f}%\n"
        f"- Volatility (std dev of daily returns): {volatility:.2f}%\n"
    )

    # Individual asset summaries
    asset_summaries = ""
    for i, symbol in enumerate(tickers):
        series = data[symbol]
        a_first = float(series.iloc[0])
        a_latest = float(series.iloc[-1])
        a_pct = ((a_latest - a_first) / a_first) * 100

        asset_summaries += (
            f"{symbol} ({weight_list[i]*100:.1f}% weight):\n"
            f"- First close: {a_first:.2f}\n"
            f"- Latest close: {a_latest:.2f}\n"
            f"- % Change: {a_pct:.2f}%\n\n"
        )

    # AI prompt
    prompt = (
        "You are a financial analyst. Provide a concise, clear, non-speculative "
        "interpretation of the following portfolio performance data.\n\n"
        f"{portfolio_summary}\n"
        "Individual asset summaries:\n"
        f"{asset_summaries}\n"
        "Focus on:\n"
        "- Relative contribution of each asset\n"
        "- Portfolio-level momentum\n"
        "- Volatility and stability\n"
        "- Concentration risks\n"
        "- Notable divergences between assets\n\n"
        "Do NOT give financial advice or predictions."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}]
    )

    commentary = response.content[0].text

    return JSONResponse({
        "symbols": tickers,
        "weights": weight_list,
        "days_analyzed": days,
        "portfolio_summary": portfolio_summary,
        "asset_summaries": asset_summaries,
        "commentary": commentary
    })
