from fastapi import UploadFile

from src.core.exceptions import NotFoundException
from src.projects.models import Project
from src.projects.repository import ProjectRepository
from src.projects.schemas import ProjectCreate, ProjectUpdate
from src.shared.cloudinary_service import CloudinaryService


class ProjectService:
    def __init__(self, repository: ProjectRepository, cloudinary: CloudinaryService):
        self.repository = repository
        self.cloudinary = cloudinary

    async def get_all(self) -> list[Project]:
        return await self.repository.get_all()

    async def get_by_id(self, project_id: int) -> Project:
        project = await self.repository.get_by_id(project_id)
        if not project:
            raise NotFoundException("Project not found")
        return project

    async def create(self, data: ProjectCreate, image: UploadFile | None) -> Project:
        image_url = ""
        if image:
            image_url = await self.cloudinary.upload(image)
        project = Project(**data.model_dump(), image_url=image_url)
        return await self.repository.create(project)

    async def update(self, project_id: int, data: ProjectUpdate) -> Project:
        project = await self.get_by_id(project_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(project, field, value)
        return await self.repository.update(project)

    async def delete(self, project_id: int) -> None:
        project = await self.get_by_id(project_id)
        await self.repository.delete(project)
