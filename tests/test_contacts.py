import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_all_contacts_empty(client: AsyncClient):
    response = await client.get("/api/contacts/")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_contact_not_found(client: AsyncClient):
    response = await client.get("/api/contacts/999")
    assert response.status_code == 404
