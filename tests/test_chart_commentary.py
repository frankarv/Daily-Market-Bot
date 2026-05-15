import pytest

@pytest.mark.asyncio
async def test_chart_commentary(client):
    response = await client.get(
        "/charts/commentary",
        params={"symbol": "AAPL", "days": 30},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert "summary" in data
    assert "commentary" in data
