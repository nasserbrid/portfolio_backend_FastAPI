from src.contacts.models import Contact
from src.contacts.repository import ContactRepository
from src.contacts.schemas import ContactCreate, ContactUpdate
from src.core.config import get_settings
from src.core.exceptions import NotFoundException
from src.core.logging import get_logger
from src.shared.email_service import send_contact_email

logger = get_logger(__name__)


class ContactService:
    def __init__(self, repository: ContactRepository):
        self.repository = repository

    async def get_all(self) -> list[Contact]:
        return await self.repository.get_all()

    async def get_by_id(self, contact_id: int) -> Contact:
        contact = await self.repository.get_by_id(contact_id)
        if not contact:
            logger.warning("Contact not found: id=%d", contact_id)
            raise NotFoundException("Contact not found")
        return contact

    async def create(self, data: ContactCreate) -> Contact:
        contact = Contact(**data.model_dump())
        saved = await self.repository.create(contact)
        logger.info("Contact created: id=%d, from='%s'", saved.id, saved.email)
        try:
            await send_contact_email(saved, get_settings())
            logger.info("Email sent for contact id=%d", saved.id)
        except Exception:
            logger.exception("Failed to send email for contact id=%d", saved.id)
        return saved

    async def update(self, contact_id: int, data: ContactUpdate) -> Contact:
        contact = await self.get_by_id(contact_id)
        for field, value in data.model_dump().items():
            setattr(contact, field, value)
        updated = await self.repository.update(contact)
        logger.info("Contact updated: id=%d", contact_id)
        return updated

    async def delete(self, contact_id: int) -> None:
        contact = await self.get_by_id(contact_id)
        await self.repository.delete(contact)
        logger.info("Contact deleted: id=%d", contact_id)
