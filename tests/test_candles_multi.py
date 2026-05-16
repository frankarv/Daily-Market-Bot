import pytest

@pytest.mark.asyncio
async def test_candles_multi(client):
    response = await client.get(
        "/candles/multi",
        params={"symbol": "AAPL", "timeframe": "daily"},
    )
    assert response.status_code == 200
