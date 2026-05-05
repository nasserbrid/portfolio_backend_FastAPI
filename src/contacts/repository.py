from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.contacts.models import Contact


class ContactRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Contact]:
        result = await self.db.execute(select(Contact))
        return list(result.scalars().all())

    async def get_by_id(self, contact_id: int) -> Contact | None:
        return await self.db.get(Contact, contact_id)

    async def create(self, contact: Contact) -> Contact:
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update(self, contact: Contact) -> Contact:
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def delete(self, contact: Contact) -> None:
        await self.db.delete(contact)
        await self.db.commit()
