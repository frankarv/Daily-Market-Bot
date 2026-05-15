import io
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from anthropic import Anthropic

router = APIRouter(prefix="/portfolio", tags=["Portfolio Combined"])

client = Anthropic()

@router.get("/combined")
def portfolio_combined(
    symbols: str = Query(..., description="Comma-separated tickers, e.g. AAPL,MSFT,GOOG"),
    weights: str = Query(..., description="Comma-separated weights (must sum to 1.0), e.g. 0.4,0.3,0.3"),
    days: int = Query(180, description="Number of days of history")
):
    """
    Returns a PNG portfolio chart AND AI-generated commentary
    in a single combined response.
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

    # --- Generate chart ---
    buf = io.BytesIO()
    plt.figure(figsize=(10, 6))
    plt.plot(portfolio_series.index, portfolio_series, label="Portfolio", linewidth=2)

    for i, symbol in enumerate(tickers):
        plt.plot(data.index, normalized[symbol], linestyle="--", alpha=0.6, label=f"{symbol} (norm)")

    plt.title(f"Portfolio ({', '.join(tickers)}) — {days}-Day Performance")
    plt.xlabel("Date")
    plt.ylabel("Normalized Value")
    plt.legend()
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # --- Summary stats ---
    first = float(portfolio_series.iloc[0])
    latest = float(portfolio_series.iloc[-1])
    pct_change = ((latest - first) / first) * 100
    high = float(portfolio_series.max())
    low = float(portfolio_series.min())

    summary = (
        f"Portfolio summary ({days} days):\n"
        f"- Symbols: {tickers}\n"
        f"- Weights: {weight_list}\n"
        f"- First value: {first:.4f}\n"
        f"- Latest value: {latest:.4f}\n"
        f"- High: {high:.4f}\n"
        f"- Low: {low:.4f}\n"
        f"- % Change: {pct_change:.2f}%\n"
    )

    # --- AI Commentary ---
    prompt = (
        "You are a financial analyst. Provide a concise, clear, non-speculative "
        "interpretation of the following portfolio performance data:\n\n"
        f"{summary}\n"
        "Focus on:\n"
        "- Relative contribution of each asset\n"
        "- Portfolio-level momentum\n"
        "- Volatility and stability\n"
        "- Concentration risks\n"
        "- Notable divergences between assets\n\n"
        "Do NOT give financial advice or predictions."
    )

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    commentary = response.content[0].text

    # --- Return combined response ---
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={
            "X-Symbols": ",".join(tickers),
            "X-Weights": ",".join([str(w) for w in weight_list]),
            "X-Days": str(days),
            "X-Commentary": commentary.replace("\n", " ")
        }
    )
