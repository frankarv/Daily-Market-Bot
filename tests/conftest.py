import pytest
from httpx import AsyncClient
from api.main import app
from tests.utils.mock_anthropic import MockAnthropic

# Patch all AI routers to use MockAnthropic
from api.routers import (
    chart_commentary,
    chart_commentary_multi,
    portfolio_commentary,
    portfolio_risk,
    chart_combined,
    chart_combined_multi,
    trend_classification,
    trend_strength,
    portfolio_combined,
)

@pytest.fixture(autouse=True)
def patch_anthropic(monkeypatch):
    # Replace the client in each AI-using router
    for module in [
        chart_commentary,
        chart_commentary_multi,
        portfolio_commentary,
        portfolio_risk,
        chart_combined,
        chart_combined_multi,
        trend_classification,
        trend_strength,
        portfolio_combined,
    ]:
        if hasattr(module, "client"):
            monkeypatch.setattr(module, "client", MockAnthropic())
    yield


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
