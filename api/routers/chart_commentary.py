import yfinance as yf
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from anthropic import Anthropic

router = APIRouter(prefix="/charts", tags=["AI Commentary"])

client = Anthropic()

@router.get("/commentary")
def chart_commentary(
    symbol: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    days: int = Query(30, description="Number of days of history to analyze")
):
    """
    Returns AI-generated commentary on recent price action for the given symbol.
    """
    data = yf.download(symbol, period=f"{days}d", interval="1d")

    if data.empty:
        return {"error": f"No data found for symbol {symbol}"}

    # Extract summary stats
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

    # Send to Claude for commentary
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
        model="claude-3-sonnet-20240229",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    commentary = response.content[0].text

    return JSONResponse({
        "symbol": symbol.upper(),
        "days_analyzed": days,
        "summary": summary,
        "commentary": commentary
    })
