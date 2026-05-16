import io
import yfinance as yf
import mplfinance as mpf
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/candles", tags=["Candlestick Charts"])

INTRADAY_MAP = {
    "1m": ("1d", "1m"),
    "5m": ("5d", "5m"),
    "15m": ("5d", "15m"),
    "30m": ("1mo", "30m"),
    "1h": ("1mo", "60m")
}

@router.get("/intraday")
def intraday_candles(
    symbol: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    interval: str = Query(
        "5m",
        description="Intraday interval: 1m, 5m, 15m, 30m, 1h",
        regex="^(1m|5m|15m|30m|1h)$"
    )
):
    """
    Returns a PNG intraday candlestick chart for the given ticker symbol.
    """
    period, yf_interval = INTRADAY_MAP[interval]

    data = yf.download(symbol, period=period, interval=yf_interval, multi_level_index=False)

    if data.empty:
        return {"error": f"No intraday data found for {symbol} ({interval})"}

    buf = io.BytesIO()

    mpf.plot(
        data,
        type="candle",
        style="charles",
        title=f"{symbol.upper()} — Intraday {interval} Candlestick Chart",
        ylabel="Price (USD)",
        volume=True,
        savefig=buf
    )

    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
