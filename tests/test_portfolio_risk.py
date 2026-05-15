import pytest

@pytest.mark.asyncio
async def test_portfolio_risk_metrics(client):
    response = await client.get(
        "/portfolio/risk",
        params={
            "symbols": "AAPL,MSFT",
            "weights": "0.5,0.5",
            "days": 180,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    metrics = data["metrics"]
    for key in [
        "average_daily_return",
        "volatility",
        "downside_volatility",
        "sharpe_ratio",
        "sortino_ratio",
        "max_drawdown",
        "calmar_ratio",
    ]:
        assert key in metrics
