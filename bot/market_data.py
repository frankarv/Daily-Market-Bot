import yfinance as yf
from datetime import datetime

INDEX_TICKERS = {
    "S&P 500": "^GSPC",
    "Nasdaq": "^IXIC",
    "Dow Jones": "^DJI",
    "Russell 2000": "^RUT",
    "VIX": "^VIX",
}

def fetch_index_snapshot():
    data = {}
    for name, ticker in INDEX_TICKERS.items():
        t = yf.Ticker(ticker)
        hist = t.history(period="2d")
        if len(hist) < 2:
            continue
        latest = hist.iloc[-1]
        prev = hist.iloc[-2]
        close = float(latest["Close"])
        prev_close = float(prev["Close"])
        change = close - prev_close
        pct = (change / prev_close) * 100
        data[name] = {
            "ticker": ticker,
            "close": round(close, 2),
            "change": round(change, 2),
            "pct_change": round(pct, 2),
        }
    return {
        "as_of": datetime.utcnow().isoformat() + "Z",
        "indices": data,
    }
