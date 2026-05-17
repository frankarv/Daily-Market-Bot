import io
import matplotlib.pyplot as plt
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from bot.agents.tools import get_indices, get_sector_performance

router = APIRouter(prefix="/charts", tags=["Charts"])

@router.get("/indices")
def chart_indices():
    """
    Returns a PNG chart of major index closing prices.
    """
    data = get_indices()
    entries = [(item["symbol"], item["close"]) for item in data["indices"] if item["close"] is not None]

    if not entries:
        return {"error": "No index data available"}

    names, values = zip(*entries)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(names, values, color="skyblue")
    ax.set_title("Major Index Close Prices")
    ax.set_ylabel("Price (USD)")
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")


@router.get("/sectors")
def chart_sectors():
    """
    Returns a PNG chart of sector ETF performance.
    """
    data = get_sector_performance()
    entries = [(item["name"], item["change_1d_pct"]) for item in data["sectors"] if item["change_1d_pct"] is not None]

    if not entries:
        return {"error": "No sector data available"}

    names, values = zip(*entries)

    fig, ax = plt.subplots(figsize=(10, 5))
    colors = ["tomato" if v < 0 else "lightgreen" for v in values]
    ax.barh(names, values, color=colors)
    ax.set_title("Sector Performance")
    ax.set_xlabel("Daily % Change (%)")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
