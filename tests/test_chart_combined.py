import pytest

@pytest.mark.asyncio
async def test_chart_combined_png(client):
    response = await client.get(
        "/charts/combined",
        params={"symbol": "AAPL", "days": 30},
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert "X-Commentary" in response.headers
    assert len(response.content) > 0
