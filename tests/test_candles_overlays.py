import pytest

@pytest.mark.asyncio
async def test_candles_overlays_png(client):
    response = await client.get(
        "/candles/overlays",
        params={"symbol": "AAPL", "sma": 20, "ema": 20, "bollinger": 20},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert len(response.content) > 0
