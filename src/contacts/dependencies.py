from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.repository import ContactRepository
from src.contacts.service import ContactService
from src.core.database import get_db


def get_contact_repository(db: AsyncSession = Depends(get_db)) -> ContactRepository:
    return ContactRepository(db)


def get_contact_service(
    repository: ContactRepository = Depends(get_contact_repository),
) -> ContactService:
    return ContactService(repository)
