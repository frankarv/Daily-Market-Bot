import pytest

@pytest.mark.asyncio
async def test_trend_classification(client):
    response = await client.get(
        "/charts/trend",
        params={"symbol": "AAPL", "days": 60},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["trend"] in ["Uptrend", "Downtrend", "Sideways / Consolidation"]
    assert "commentary" in data
