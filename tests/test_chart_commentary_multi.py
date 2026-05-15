import pytest

@pytest.mark.asyncio
async def test_chart_commentary_multi(client):
    response = await client.get(
        "/charts/commentary-multi",
        params={"symbols": "AAPL,MSFT", "days": 30},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbols"] == ["AAPL", "MSFT"]
    assert "summaries" in data
    assert "commentary" in data
