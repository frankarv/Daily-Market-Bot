import yfinance as yf
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from anthropic import Anthropic

router = APIRouter(prefix="/charts", tags=["AI Commentary"])

client = Anthropic()

@router.get("/commentary-multi")
def chart_commentary_multi(
    symbols: str = Query(..., description="Comma-separated tickers, e.g. AAPL,MSFT,GOOG"),
    days: int = Query(30, description="Number of days of history to analyze")
):
    """
    Returns AI-generated comparative commentary for multiple symbols.
    """
    tickers = [s.strip().upper() for s in symbols.split(",")]

    summaries = {}
    summary_text = ""

    for symbol in tickers:
        data = yf.download(symbol, period=f"{days}d", interval="1d")

        if data.empty:
            summaries[symbol] = {"error": f"No data found for {symbol}"}
            continue

        close_prices = data["Close"]
        high = float(close_prices.max())
        low = float(close_prices.min())
        latest = float(close_prices.iloc[-1])
        first = float(close_prices.iloc[0])
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

    # AI prompt
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

    return JSONResponse({
        "symbols": tickers,
        "days_analyzed": days,
        "summaries": summaries,
        "commentary": commentary
    })
