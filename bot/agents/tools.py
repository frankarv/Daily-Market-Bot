# bot/agents/tools.py
import yfinance as yf
import math
from datetime import datetime, timedelta

# -----------------------------
# Helpers
# -----------------------------

def safe_float(x):
    """Convert to float, returning None for NaN, inf, or invalid values."""
    try:
        if x is None:
            return None
        if isinstance(x, str):
            return None
        if math.isnan(x) or math.isinf(x):
            return None
        return float(x)
    except:
        return None


def safe_dict(d):
    """Ensure all values in a dict are JSON-safe floats or None."""
    return {k: safe_float(v) for k, v in d.items()}


# -----------------------------
# Index Data
# -----------------------------

def get_indices():
    """
    Fetch basic data for major indices.
    Returns JSON-safe structure:
    {
        "as_of": "...",
        "indices": [
            {"symbol": "...", "close": float_or_none},
            ...
        ]
    }
    """
    symbols = ["^GSPC", "^NDX", "^DJI", "^RUT"]

    try:
        data = yf.download(
            symbols,
            period="1d",
            interval="1d",
            auto_adjust=True,
            progress=False
        )
    except Exception:
        # Total failure fallback
        return {
            "as_of": datetime.utcnow().isoformat(),
            "indices": [{"symbol": s, "close": None} for s in symbols],
        }

    # If data is empty or partially missing
    if data.empty or "Close" not in data:
        return {
            "as_of": datetime.utcnow().isoformat(),
            "indices": [{"symbol": s, "close": None} for s in symbols],
        }

    # Extract last close values safely
    try:
        latest = data["Close"].iloc[-1].to_dict()
        latest = safe_dict(latest)
    except Exception:
        latest = {s: None for s in symbols}

    return {
        "as_of": datetime.utcnow().isoformat(),
        "indices": [
            {"symbol": s, "close": latest.get(s)}
            for s in symbols
        ],
    }


# -----------------------------
# Sector Performance
# -----------------------------

def get_sector_performance():
    """
    Fetch sector ETF performance (1-day % change).
    Returns JSON-safe structure:
    {
        "as_of": "...",
        "sectors": [
            {"symbol": "...", "name": "...", "change_1d_pct": float_or_none},
            ...
        ]
    }
    """
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

    try:
        data = yf.download(
            list(sectors.keys()),
            start=start,
            end=end,
            interval="1d",
            auto_adjust=True,
            progress=False
        )
    except Exception:
        # Total failure fallback
        return {
            "as_of": datetime.utcnow().isoformat(),
            "sectors": [
                {"symbol": s, "name": n, "change_1d_pct": None}
                for s, n in sectors.items()
            ],
        }

    # If missing or empty
    if data.empty or "Close" not in data:
        return {
            "as_of": datetime.utcnow().isoformat(),
            "sectors": [
                {"symbol": s, "name": n, "change_1d_pct": None}
                for s, n in sectors.items()
            ],
        }

    try:
        close = data["Close"]
        latest = close.iloc[-1]
        prev = close.iloc[-2]
    except Exception:
        # Not enough rows
        return {
            "as_of": datetime.utcnow().isoformat(),
            "sectors": [
                {"symbol": s, "name": n, "change_1d_pct": None}
                for s, n in sectors.items()
            ],
        }

    perf = []
    for symbol, name in sectors.items():
        try:
            pct = ((latest[symbol] / prev[symbol]) - 1) * 100
            pct = safe_float(pct)
        except Exception:
            pct = None

        perf.append({
            "symbol": symbol,
            "name": name,
            "change_1d_pct": pct,
        })

    return {
        "as_of": datetime.utcnow().isoformat(),
        "sectors": perf,
    }


# -----------------------------
# Save Report
# -----------------------------

def save_report(markdown: str, path: str = "market-report.md"):
    """Save the final report to disk."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(markdown)
        return {"path": path}
    except Exception as e:
        return {"path": None, "error": str(e)}
