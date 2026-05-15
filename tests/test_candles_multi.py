import pytest

@pytest.mark.asyncio
async def test_candles_multi(client):
    response = await client.get(
        "/candles/multi",
        params={"symbols": "AAPL,MSFT"},
    )
    assert response.status_code == 200
