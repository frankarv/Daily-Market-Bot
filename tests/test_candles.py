import pytest

@pytest.mark.asyncio
async def test_candles_basic(client):
    response = await client.get("/candles/daily", params={"symbol": "AAPL"})
    assert response.status_code == 200
