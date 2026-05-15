import pytest

@pytest.mark.asyncio
async def test_candles_intraday(client):
    response = await client.get(
        "/candles/intraday",
        params={"symbol": "AAPL", "interval": "5m"},
    )
    assert response.status_code == 200
