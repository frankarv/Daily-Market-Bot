import yfinance as yf
import numpy as np
import pandas as pd
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
import os
from anthropic import Anthropic

router = APIRouter(prefix="/portfolio", tags=["Portfolio Risk Metrics"])

client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))

def max_drawdown(series):
    cumulative = series.cummax()
    drawdown = (series - cumulative) / cumulative
    return float(drawdown.min())

@router.get("/risk")
def portfolio_risk_metrics(
    symbols: str = Query(..., description="Comma-separated tickers, e.g. AAPL,MSFT,GOOG"),
    weights: str = Query(..., description="Comma-separated weights (must sum to 1.0), e.g. 0.4,0.3,0.3"),
    days: int = Query(180, description="Number of days of history to analyze")
):
    """
    Returns portfolio risk metrics (Sharpe, Sortino, Max Drawdown, etc.)
    plus AI-generated interpretation.
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

    # Compute normalized portfolio value
    normalized = data / data.iloc[0]
    portfolio_series = (normalized * weight_list).sum(axis=1)

    # Daily returns
    returns = portfolio_series.pct_change().dropna()

    # Risk metrics
    avg_return = float(returns.mean())
    volatility = float(returns.std())
    downside_returns = returns[returns < 0]
    downside_vol = float(downside_returns.std()) if len(downside_returns) > 0 else 0.0

    sharpe = avg_return / volatility if volatility > 0 else 0.0
    sortino = avg_return / downside_vol if downside_vol > 0 else 0.0

    mdd = max_drawdown(portfolio_series)
    calmar = (portfolio_series.iloc[-1] / portfolio_series.iloc[0] - 1) / abs(mdd) if mdd != 0 else 0.0

    # Summary for AI
    summary = (
        f"Portfolio risk metrics ({days} days):\n"
        f"- Symbols: {tickers}\n"
        f"- Weights: {weight_list}\n"
        f"- Average daily return: {avg_return:.4f}\n"
        f"- Volatility (std dev): {volatility:.4f}\n"
        f"- Downside volatility: {downside_vol:.4f}\n"
        f"- Sharpe ratio: {sharpe:.3f}\n"
        f"- Sortino ratio: {sortino:.3f}\n"
        f"- Max drawdown: {mdd:.3f}\n"
        f"- Calmar ratio: {calmar:.3f}\n"
    )

    # AI Interpretation
    prompt = (
        "You are a financial analyst. Interpret the following portfolio risk metrics "
        "in a concise, non-speculative way:\n\n"
        f"{summary}\n"
        "Focus on:\n"
        "- Risk-adjusted performance\n"
        "- Volatility regime\n"
        "- Drawdown behavior\n"
        "- Stability vs. risk-taking\n"
        "- What stands out\n\n"
        "Do NOT give financial advice or predictions."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    commentary = response.content[0].text

    return JSONResponse({
        "symbols": tickers,
        "weights": weight_list,
        "days_analyzed": days,
        "metrics": {
            "average_daily_return": avg_return,
            "volatility": volatility,
            "downside_volatility": downside_vol,
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown": mdd,
            "calmar_ratio": calmar
        },
        "summary": summary,
        "commentary": commentary
    })
