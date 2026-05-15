import pytest

@pytest.mark.asyncio
async def test_chart_combined_multi_png(client):
    response = await client.get(
        "/charts/combined-multi",
        params={"symbols": "AAPL,MSFT", "days": 60},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert "X-Commentary" in response.headers
    assert len(response.content) > 0
