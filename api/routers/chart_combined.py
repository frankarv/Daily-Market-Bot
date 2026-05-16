import io
import yfinance as yf
import mplfinance as mpf
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse
import os
from anthropic import Anthropic

router = APIRouter(prefix="/charts", tags=["Combined Chart + Commentary"])

client = Anthropic(api_key=os.environ.get("CLAUDE_API_KEY") or os.environ.get("ANTHROPIC_API_KEY"))

@router.get("/combined")
def combined_chart_and_commentary(
    symbol: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    days: int = Query(30, description="Number of days of history")
):
    """
    Returns a PNG candlestick chart AND AI-generated commentary
    in a single multipart response.
    """
    data = yf.download(symbol, period=f"{days}d", interval="1d", multi_level_index=False)

    if data.empty:
        return {"error": f"No data found for symbol {symbol}"}

    # --- Generate chart ---
    buf = io.BytesIO()
    mpf.plot(
        data,
        type="candle",
        style="charles",
        title=f"{symbol.upper()} — {days}-Day Candlestick Chart",
        ylabel="Price (USD)",
        volume=True,
        savefig=buf
    )
    buf.seek(0)

    # --- Compute summary stats ---
    close_prices = data["Close"]
    high = float(close_prices.max())
    low = float(close_prices.min())
    latest = float(close_prices.iloc[-1])
    first = float(close_prices.iloc[0])
    pct_change = ((latest - first) / first) * 100

    summary = (
        f"{symbol} price summary over the last {days} days:\n"
        f"- First close: {first:.2f}\n"
        f"- Latest close: {latest:.2f}\n"
        f"- High: {high:.2f}\n"
        f"- Low: {low:.2f}\n"
        f"- % Change: {pct_change:.2f}%\n"
    )

    # --- AI Commentary ---
    prompt = (
        "You are a financial analyst. Provide a concise, clear, "
        "non-speculative interpretation of the following price data:\n\n"
        f"{summary}\n"
        "Focus on:\n"
        "- Trend direction\n"
        "- Volatility\n"
        "- Momentum\n"
        "- Key levels\n"
        "- What stands out\n\n"
        "Do NOT give financial advice or predictions."
    )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    commentary = response.content[0].text

    # --- Return multipart response ---
    return StreamingResponse(
        buf,
        media_type="image/png",
        headers={
            "X-Symbol": symbol.upper(),
            "X-Days": str(days),
            "X-Commentary": commentary.replace("\n", " ")
        }
    )
