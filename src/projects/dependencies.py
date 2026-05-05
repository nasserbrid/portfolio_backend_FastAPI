from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.projects.repository import ProjectRepository
from src.projects.service import ProjectService
from src.shared.cloudinary_service import CloudinaryService


def get_project_repository(db: AsyncSession = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)


def get_cloudinary_service() -> CloudinaryService:
    return CloudinaryService()


def get_project_service(
    repository: ProjectRepository = Depends(get_project_repository),
    cloudinary: CloudinaryService = Depends(get_cloudinary_service),
) -> ProjectService:
    return ProjectService(repository, cloudinary)
