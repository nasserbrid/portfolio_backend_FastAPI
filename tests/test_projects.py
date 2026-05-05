from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from src.core.exceptions import NotFoundException
from src.projects.models import Project
from src.projects.repository import ProjectRepository
from src.projects.schemas import ProjectCreate, ProjectUpdate
from src.projects.service import ProjectService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_project(**kwargs) -> Project:
    defaults = {
        "id": 1,
        "title": "Mon projet",
        "description": "Une description",
        "skills": "Python, FastAPI",
        "image_url": "https://res.cloudinary.com/demo/image.jpg",
    }
    for key, value in {**defaults, **kwargs}.items():
        setattr(p := Project(), key, value)
    return p


def make_service(projects: list[Project] | None = None) -> tuple[ProjectService, AsyncMock]:
    """Retourne un ProjectService avec repository mocké."""
    repo = AsyncMock(spec=ProjectRepository)
    cloudinary = MagicMock()
    cloudinary.upload = AsyncMock(return_value="https://cloudinary.com/uploaded.jpg")

    if projects is not None:
        repo.get_all.return_value = projects

    service = ProjectService(repository=repo, cloudinary=cloudinary)
    return service, repo


# ---------------------------------------------------------------------------
# Tests unitaires — Service (logique métier isolée)
# ---------------------------------------------------------------------------

class TestProjectService:

    @pytest.mark.asyncio
    async def test_get_by_id_raises_not_found(self):
        service, repo = make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.get_by_id(999)

    @pytest.mark.asyncio
    async def test_create_uses_image_url_when_no_file(self):
        service, repo = make_service()
        project = make_project(image_url="https://cloudinary.com/direct.jpg")
        repo.create.return_value = project

        data = ProjectCreate(
            title="Test",
            description="Desc",
            skills="Python",
            image_url="https://cloudinary.com/direct.jpg",
        )
        result = await service.create(data, image=None)

        # Cloudinary ne doit PAS être appelé
        service.cloudinary.upload.assert_not_called()
        assert result.image_url == "https://cloudinary.com/direct.jpg"

    @pytest.mark.asyncio
    async def test_create_file_upload_takes_priority_over_url(self):
        service, repo = make_service()
        project = make_project(image_url="https://cloudinary.com/uploaded.jpg")
        repo.create.return_value = project

        data = ProjectCreate(
            title="Test",
            description="Desc",
            skills="Python",
            image_url="https://cloudinary.com/direct.jpg",
        )
        fake_file = MagicMock()
        result = await service.create(data, image=fake_file)

        # Cloudinary DOIT être appelé — le fichier prime sur l'URL
        service.cloudinary.upload.assert_called_once_with(fake_file)

    @pytest.mark.asyncio
    async def test_update_raises_not_found(self):
        service, repo = make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.update(999, ProjectUpdate(title="X", description="Y", skills="Z"))

    @pytest.mark.asyncio
    async def test_delete_raises_not_found(self):
        service, repo = make_service()
        repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await service.delete(999)


# ---------------------------------------------------------------------------
# Tests d'intégration — Router (HTTP complet + DB SQLite)
# ---------------------------------------------------------------------------

class TestProjectsAPI:

    @pytest.mark.asyncio
    async def test_get_all_returns_empty_list(self, client: AsyncClient):
        response = await client.get("/api/projects/")
        assert response.status_code == 200
        assert response.json() == []

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, client: AsyncClient):
        response = await client.get("/api/projects/999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_project_with_image_url(self, client: AsyncClient):
        response = await client.post(
            "/api/projects/",
            data={
                "title": "Portfolio FastAPI",
                "description": "Backend en Python",
                "skills": "Python, FastAPI, PostgreSQL",
                "image_url": "https://res.cloudinary.com/demo/image.jpg",
            },
        )
        assert response.status_code == 201
        body = response.json()
        assert body["title"] == "Portfolio FastAPI"
        assert body["imageUrl"] == "https://res.cloudinary.com/demo/image.jpg"

    @pytest.mark.asyncio
    async def test_get_all_returns_created_project(self, client: AsyncClient):
        await client.post(
            "/api/projects/",
            data={
                "title": "Mon projet",
                "description": "Description",
                "skills": "Python",
                "image_url": "https://res.cloudinary.com/demo/image.jpg",
            },
        )
        response = await client.get("/api/projects/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    @pytest.mark.asyncio
    async def test_update_project(self, client: AsyncClient):
        create = await client.post(
            "/api/projects/",
            data={
                "title": "Ancien titre",
                "description": "Desc",
                "skills": "Python",
                "image_url": "https://res.cloudinary.com/demo/image.jpg",
            },
        )
        project_id = create.json()["id"]

        response = await client.put(
            f"/api/projects/{project_id}",
            json={
                "title": "Nouveau titre",
                "description": "Desc",
                "skills": "Python, FastAPI",
            },
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Nouveau titre"

    @pytest.mark.asyncio
    async def test_delete_project(self, client: AsyncClient):
        create = await client.post(
            "/api/projects/",
            data={
                "title": "À supprimer",
                "description": "Desc",
                "skills": "Python",
                "image_url": "https://res.cloudinary.com/demo/image.jpg",
            },
        )
        project_id = create.json()["id"]

        response = await client.delete(f"/api/projects/{project_id}")
        assert response.status_code == 204

        response = await client.get(f"/api/projects/{project_id}")
        assert response.status_code == 404
