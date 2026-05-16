import io
import yfinance as yf
import mplfinance as mpf
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/candles", tags=["Candlestick Charts"])

@router.get("/daily")
def candlestick_chart(
    symbol: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    days: int = Query(30, description="Number of days of history")
):
    """
    Returns a PNG candlestick chart for the given ticker symbol.
    """
    data = yf.download(symbol, period=f"{days}d", interval="1d", multi_level_index=False)

    if data.empty:
        return {"error": f"No data found for symbol {symbol}"}

    buf = io.BytesIO()

    mpf.plot(
        data,
        type="candle",
        style="charles",
        title=f"{symbol} — {days}-Day Candlestick Chart",
        ylabel="Price (USD)",
        volume=True,
        savefig=buf
    )

    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
