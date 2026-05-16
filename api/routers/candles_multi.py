import io
import yfinance as yf
import mplfinance as mpf
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/candles", tags=["Candlestick Charts"])

TIMEFRAME_MAP = {
    "daily": ("1d", "1d"),
    "weekly": ("3mo", "1wk"),
    "monthly": ("1y", "1mo")
}

@router.get("/multi")
def multi_timeframe_candles(
    symbol: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    timeframe: str = Query(
        "daily",
        description="Timeframe: daily, weekly, or monthly",
        regex="^(daily|weekly|monthly)$"
    )
):
    """
    Returns a PNG candlestick chart for the given ticker symbol
    across multiple timeframes (daily, weekly, monthly).
    """
    period, interval = TIMEFRAME_MAP[timeframe]

    data = yf.download(symbol, period=period, interval=interval, multi_level_index=False)

    if data.empty:
        return {"error": f"No data found for symbol {symbol} ({timeframe})"}

    buf = io.BytesIO()

    mpf.plot(
        data,
        type="candle",
        style="charles",
        title=f"{symbol.upper()} — {timeframe.capitalize()} Candlestick Chart",
        ylabel="Price (USD)",
        volume=True,
        savefig=buf
    )

    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
