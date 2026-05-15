import pytest

@pytest.mark.asyncio
async def test_portfolio_combined_png(client):
    response = await client.get(
        "/portfolio/combined",
        params={
            "symbols": "AAPL,MSFT",
            "weights": "0.5,0.5",
            "days": 180,
        },
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert "X-Commentary" in response.headers
    assert len(response.content) > 0
