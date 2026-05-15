import io
import matplotlib.pyplot as plt
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from bot.tools.market_data import get_indices, get_sector_performance

router = APIRouter(prefix="/charts", tags=["Charts"])

@router.get("/indices")
def chart_indices():
    """
    Returns a PNG chart of major index performance.
    """
    data = get_indices()

    fig, ax = plt.subplots(figsize=(8, 4))
    names = list(data.keys())
    values = [data[k] for k in names]

    ax.bar(names, values, color="skyblue")
    ax.set_title("Major Index Performance")
    ax.set_ylabel("Daily % Change")
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

    fig, ax = plt.subplots(figsize=(10, 5))
    names = list(data.keys())
    values = [data[k] for k in names]

    ax.barh(names, values, color="lightgreen")
    ax.set_title("Sector Performance")
    ax.set_xlabel("Daily % Change")
    ax.grid(axis="x", linestyle="--", alpha=0.4)

    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png")
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/png")
