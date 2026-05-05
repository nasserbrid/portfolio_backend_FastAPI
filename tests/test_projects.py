import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_all_projects_empty(client: AsyncClient):
    response = await client.get("/api/projects/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_project_not_found(client: AsyncClient):
    response = await client.get("/api/projects/999")
    assert response.status_code == 404
