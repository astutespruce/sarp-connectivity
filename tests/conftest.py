from httpx import ASGITransport, AsyncClient
import pytest

from api.server import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(name="client", scope="session")
async def client_fixture():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://localhost:5000") as client:
        yield client
