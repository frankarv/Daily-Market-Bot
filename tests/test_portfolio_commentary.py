import pytest

@pytest.mark.asyncio
async def test_portfolio_commentary(client):
    response = await client.get(
        "/portfolio/commentary",
        params={
            "symbols": "AAPL,MSFT",
            "weights": "0.5,0.5",
            "days": 60,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["symbols"] == ["AAPL", "MSFT"]
    assert "portfolio_summary" in data
    assert "asset_summaries" in data
    assert "commentary" in data
