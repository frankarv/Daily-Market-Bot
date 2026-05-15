import io
import yfinance as yf
import matplotlib.pyplot as plt
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse, JSONResponse
from anthropic import Anthropic

router = APIRouter(prefix="/charts", tags=["Combined Chart + Commentary"])

client = Anthropic()

@router.get("/combined-multi")
def combined_multi_chart_and_commentary(
    symbols: str = Query(..., description="Comma-separated tickers, e.g. AAPL,MSFT,GOOG"),
    days: int = Query(60, description="Number of days of history")
):
    """
    Returns a combined PNG chart AND AI-generated comparative commentary
    for multiple symbols.
    """
    tickers = [s.strip().upper() for s in symbols.split(",")]

    # --- Download data ---
    data = yf.download(tickers, period=f"{days}d", interval="1d")["Close"]

    if data.empty:
        return {"error": "No data found for the provided symbols"}

    # --- Generate combined chart ---
    buf = io.BytesIO()
    plt.figure(figsize=(10, 6))

    for symbol in tickers:
        plt.plot(data.index, data[symbol], label=symbol)

    plt.title(f"{', '.join(tickers)} — {days}-Day Price Comparison")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    # --- Compute summary stats ---
    summaries = {}
    summary_text = ""

    for symbol in tickers:
        series = data[symbol]
        first = float(series.iloc[0])
        latest = float(series.iloc[-1])
        high = float(series.max())
        low = float(series.min())
        pct_change = ((latest - first) / first) * 100

        summary = (
            f"{symbol} ({days} days):\n"
            f"- First close: {first:.2f}\n"
            f"- Latest close: {latest:.2f}\n"
            f"- High: {high:.2f}\n"
            f"- Low: {low:.2f}\n"
            f"- % Change: {pct_change:.2f}%\n"
        )

        summaries[symbol] = summary
        summary_text += summary + "\n"

    # --- AI Commentary ---
    prompt = (
        "You are a financial analyst. Compare the following assets based on their "
        "recent price action. Provide a concise, clear, non-speculative interpretation.\n\n"
        f"{summary_text}\n"
        "Focus on:\n"
        "- Relative strength\n"
        "- Volatility differences\n"
        "- Momentum comparison\n"
        "- Notable divergences\n"
        "- What stands out across the group\n\n"
        "Do NOT give financial advice or predictions."
    )

    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )

    commentary = response.content[0].text

    # --- Return multipart response ---
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={
            "X-Symbols": ",".join(tickers),
            "X-Days": str(days),
            "X-Commentary": commentary.replace("\n", " ")
        }
    )
