# bot/agents/tools.py
import yfinance as yf
from datetime import datetime, timedelta

def get_indices():
    """Fetch basic data for major indices."""
    symbols = ["^GSPC", "^NDX", "^DJI", "^RUT"]
    data = yf.download(symbols, period="1d", interval="1d", auto_adjust=True)
    latest = data["Close"].iloc[-1].to_dict()

    return {
        "as_of": datetime.utcnow().isoformat(),
        "indices": [
            {"symbol": s, "close": float(latest[s])}
            for s in symbols
        ],
    }

def get_sector_performance():
    """Fetch sector ETF performance (1-day % change)."""
    sectors = {
        "XLF": "Financials",
        "XLK": "Technology",
        "XLE": "Energy",
        "XLY": "Consumer Discretionary",
        "XLP": "Consumer Staples",
        "XLV": "Health Care",
        "XLI": "Industrials",
        "XLU": "Utilities",
        "XLRE": "Real Estate",
        "XLB": "Materials",
        "XLC": "Communication Services",
    }

    end = datetime.utcnow()
    start = end - timedelta(days=3)

    data = yf.download(list(sectors.keys()), start=start, end=end, interval="1d", auto_adjust=True)["Close"]
    latest = data.iloc[-1]
    prev = data.iloc[-2]

    perf = []
    for symbol, name in sectors.items():
        pct = (latest[symbol] / prev[symbol] - 1) * 100
        perf.append({
            "symbol": symbol,
            "name": name,
            "change_1d_pct": float(pct),
        })

    return {
        "as_of": datetime.utcnow().isoformat(),
        "sectors": perf,
    }

def save_report(markdown: str, path: str = "market-report.md"):
    """Save the final report to disk."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(markdown)
    return {"path": path}
