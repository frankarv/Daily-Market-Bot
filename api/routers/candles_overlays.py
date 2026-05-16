import io
import yfinance as yf
import mplfinance as mpf
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/candles", tags=["Candlestick Charts"])

@router.get("/overlays")
def candlestick_overlays(
    symbol: str = Query(..., description="Ticker symbol, e.g. AAPL"),
    sma: int = Query(20, description="Simple Moving Average window"),
    ema: int = Query(20, description="Exponential Moving Average window"),
    bollinger: int = Query(20, description="Bollinger Bands window")
):
    """
    Returns a PNG candlestick chart with SMA, EMA, and Bollinger Bands overlays.
    """
    data = yf.download(symbol, period="6mo", interval="1d", multi_level_index=False)

    if data.empty:
        return {"error": f"No data found for symbol {symbol}"}

    # Calculate overlays
    data["SMA"] = data["Close"].rolling(window=sma).mean()
    data["EMA"] = data["Close"].ewm(span=ema, adjust=False).mean()
    data["BB_MID"] = data["Close"].rolling(window=bollinger).mean()
    data["BB_STD"] = data["Close"].rolling(window=bollinger).std()
    data["BB_UPPER"] = data["BB_MID"] + (data["BB_STD"] * 2)
    data["BB_LOWER"] = data["BB_MID"] - (data["BB_STD"] * 2)

    # Build overlay list for mplfinance
    overlays = [
        mpf.make_addplot(data["SMA"], color="blue"),
        mpf.make_addplot(data["EMA"], color="orange"),
        mpf.make_addplot(data["BB_UPPER"], color="green"),
        mpf.make_addplot(data["BB_MID"], color="gray"),
        mpf.make_addplot(data["BB_LOWER"], color="green"),
    ]

    buf = io.BytesIO()

    mpf.plot(
        data,
        type="candle",
        style="charles",
        title=f"{symbol.upper()} — Candlestick with SMA/EMA/Bollinger",
        ylabel="Price (USD)",
        volume=True,
        addplot=overlays,
        savefig=buf
    )

    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
