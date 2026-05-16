import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from api.main import app
from tests.utils.mock_anthropic import MockAnthropic

import api.routers.chart_combined
import api.routers.chart_combined_multi
import api.routers.chart_commentary
import api.routers.chart_commentary_multi
import api.routers.portfolio_combined
import api.routers.portfolio_commentary
import api.routers.portfolio_risk
import api.routers.trend_classification
import api.routers.trend_strength

_AI_MODULES = [
    api.routers.chart_combined,
    api.routers.chart_combined_multi,
    api.routers.chart_commentary,
    api.routers.chart_commentary_multi,
    api.routers.portfolio_combined,
    api.routers.portfolio_commentary,
    api.routers.portfolio_risk,
    api.routers.trend_classification,
    api.routers.trend_strength,
]

@pytest.fixture(autouse=True)
def mock_ai_client(monkeypatch):
    mock = MockAnthropic()
    for module in _AI_MODULES:
        monkeypatch.setattr(module, "client", mock)

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
