import pytest

@pytest.mark.asyncio
async def test_trend_strength_score(client):
    response = await client.get(
        "/charts/trend-strength",
        params={"symbol": "AAPL", "days": 90},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    score = data["trend_strength_score"]
    assert 0 <= score <= 100
    assert "metrics" in data
    assert "commentary" in data
