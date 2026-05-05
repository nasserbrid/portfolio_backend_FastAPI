from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from src.contacts.models import Contact
from src.contacts.repository import ContactRepository
from src.contacts.schemas import ContactCreate, ContactUpdate
from src.contacts.service import ContactService
from src.core.exceptions import NotFoundException


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_contact(**kwargs) -> Contact:
    defaults = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
        "message": "Bonjour !",
        "created_at": datetime.now(timezone.utc),
    }
    c = Contact()
    for key, value in {**defaults, **kwargs}.items():
        setattr(c, key, value)
    return c


def make_service() -> tuple[ContactService, AsyncMock]:
    """Retourne un ContactService avec repository mocké."""
    repo = AsyncMock(spec=ContactRepository)
    service = ContactService(repository=repo)
    return service, repo


# ---------------------------------------------------------------------------
# Tests unitaires — Service (logique métier isolée)
# ---------------------------------------------------------------------------

class TestContactService:

    @pytest.mark.asyncio
    async def test_get_by_id_raises_not_found(self):
        service, repo = make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_by_id(999)

    @pytest.mark.asyncio
    async def test_create_saves_contact_and_sends_email(self):
        service, repo = make_service()
        contact = make_contact()
        repo.create.return_value = contact

        data = ContactCreate(name="John Doe", email="john@example.com", message="Bonjour !")

        # On mocke l'envoi email pour ne pas appeler Gmail
        with patch("src.contacts.service.send_contact_email", new_callable=AsyncMock) as mock_email:
            result = await service.create(data)

        repo.create.assert_called_once()
        mock_email.assert_called_once()
        assert result.name == "John Doe"

    @pytest.mark.asyncio
    async def test_create_email_failure_does_not_save_twice(self):
        service, repo = make_service()
        contact = make_contact()
        repo.create.return_value = contact

        data = ContactCreate(name="John Doe", email="john@example.com", message="Bonjour !")

        with patch("src.contacts.service.send_contact_email", new_callable=AsyncMock):
            await service.create(data)

        # Le repository ne doit être appelé qu'une seule fois
        repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_raises_not_found(self):
        service, repo = make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.update(999, ContactUpdate(name="X", email="x@x.com", message="Y"))

    @pytest.mark.asyncio
    async def test_update_modifies_fields(self):
        service, repo = make_service()
        contact = make_contact()
        repo.get_by_id.return_value = contact
        repo.update.return_value = contact

        data = ContactUpdate(name="Jane Doe", email="jane@example.com", message="Nouveau message")
        await service.update(1, data)

        assert contact.name == "Jane Doe"
        assert contact.email == "jane@example.com"
        assert contact.message == "Nouveau message"

    @pytest.mark.asyncio
    async def test_delete_raises_not_found(self):
        service, repo = make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.delete(999)

    @pytest.mark.asyncio
    async def test_delete_calls_repository(self):
        service, repo = make_service()
        contact = make_contact()
        repo.get_by_id.return_value = contact

        await service.delete(1)

        repo.delete.assert_called_once_with(contact)


# ---------------------------------------------------------------------------
# Tests d'intégration — Router (HTTP complet + DB SQLite)
# ---------------------------------------------------------------------------

class TestContactsAPI:

    @pytest.mark.asyncio
    async def test_get_all_returns_empty_list(self, client: AsyncClient):
        response = await client.get("/api/contacts/")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, client: AsyncClient):
        response = await client.get("/api/contacts/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_contact(self, client: AsyncClient):
        with patch("src.contacts.service.send_contact_email", new_callable=AsyncMock):
            response = await client.post(
                "/api/contacts/",
                json={
                    "name": "John Doe",
                    "email": "john@example.com",
                    "message": "Bonjour depuis les tests !",
                },
            )
        assert response.status_code == 201
        body = response.json()
        assert body["name"] == "John Doe"
        assert body["email"] == "john@example.com"
        assert "id" in body
        assert "createdAt" in body

    @pytest.mark.asyncio
    async def test_get_all_returns_created_contact(self, client: AsyncClient):
        with patch("src.contacts.service.send_contact_email", new_callable=AsyncMock):
            await client.post(
                "/api/contacts/",
                json={"name": "John Doe", "email": "john@example.com", "message": "Test"},
            )
        response = await client.get("/api/contacts/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_update_contact(self, client: AsyncClient):
        with patch("src.contacts.service.send_contact_email", new_callable=AsyncMock):
            create = await client.post(
                "/api/contacts/",
                json={"name": "John Doe", "email": "john@example.com", "message": "Initial"},
            )
        contact_id = create.json()["id"]

        response = await client.put(
            f"/api/contacts/{contact_id}",
            json={"name": "Jane Doe", "email": "jane@example.com", "message": "Modifié"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Jane Doe"

    @pytest.mark.asyncio
    async def test_delete_contact(self, client: AsyncClient):
        with patch("src.contacts.service.send_contact_email", new_callable=AsyncMock):
            create = await client.post(
                "/api/contacts/",
                json={"name": "John Doe", "email": "john@example.com", "message": "À supprimer"},
            )
        contact_id = create.json()["id"]

        response = await client.delete(f"/api/contacts/")
        assert response.status_code == 405

        response = await client.delete(f"/api/contacts/{contact_id}")
        assert response.status_code == 204

        response = await client.get(f"/api/contacts/{contact_id}")
        assert response.status_code == 404
