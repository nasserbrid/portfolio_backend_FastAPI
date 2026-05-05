from src.contacts.models import Contact
from src.contacts.repository import ContactRepository
from src.contacts.schemas import ContactCreate, ContactUpdate
from src.core.config import get_settings
from src.core.exceptions import NotFoundException
from src.shared.email_service import send_contact_email


class ContactService:
    def __init__(self, repository: ContactRepository):
        self.repository = repository

    async def get_all(self) -> list[Contact]:
        return await self.repository.get_all()

    async def get_by_id(self, contact_id: int) -> Contact:
        contact = await self.repository.get_by_id(contact_id)
        if not contact:
            raise NotFoundException("Contact not found")
        return contact

    async def create(self, data: ContactCreate) -> Contact:
        contact = Contact(**data.model_dump())
        saved = await self.repository.create(contact)
        settings = get_settings()
        await send_contact_email(saved, settings)
        return saved

    async def update(self, contact_id: int, data: ContactUpdate) -> Contact:
        contact = await self.get_by_id(contact_id)
        for field, value in data.model_dump().items():
            setattr(contact, field, value)
        return await self.repository.update(contact)

    async def delete(self, contact_id: int) -> None:
        contact = await self.get_by_id(contact_id)
        await self.repository.delete(contact)
