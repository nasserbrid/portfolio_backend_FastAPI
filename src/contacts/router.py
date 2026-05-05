from fastapi import APIRouter, Depends, status

from src.contacts.dependencies import get_contact_service
from src.contacts.schemas import ContactCreate, ContactResponse, ContactUpdate
from src.contacts.service import ContactService

router = APIRouter(prefix="/api/contacts", tags=["contacts"])


@router.get("/", response_model=list[ContactResponse])
async def get_all(service: ContactService = Depends(get_contact_service)):
    return await service.get_all()


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_by_id(contact_id: int, service: ContactService = Depends(get_contact_service)):
    return await service.get_by_id(contact_id)


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create(data: ContactCreate, service: ContactService = Depends(get_contact_service)):
    return await service.create(data)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update(
    contact_id: int,
    data: ContactUpdate,
    service: ContactService = Depends(get_contact_service),
):
    return await service.update(contact_id, data)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(contact_id: int, service: ContactService = Depends(get_contact_service)):
    await service.delete(contact_id)
