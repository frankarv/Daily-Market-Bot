import pytest

@pytest.mark.asyncio
async def test_candles_basic(client):
    # Adjust path if your candles router uses a different one
    response = await client.get("/candles", params={"symbol": "AAPL"})
    assert response.status_code == 200
    # Could be JSON or image depending on your implementation
