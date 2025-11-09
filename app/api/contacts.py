"""Contact API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from app.services.contact_service import ContactService

router = APIRouter()


@router.post("/", response_model=ContactResponse, status_code=201)
async def create_contact(contact: ContactCreate, db: AsyncSession = Depends(get_db)):
    """Create a new contact"""
    return await ContactService.create_contact(db, contact)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: str, db: AsyncSession = Depends(get_db)):
    """Get a contact by ID"""
    contact = await ContactService.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get all contacts for a user"""
    return await ContactService.get_user_contacts(db, user_id)


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(user_id: str, query: str, db: AsyncSession = Depends(get_db)):
    """Search contacts"""
    return await ContactService.search_contacts(db, user_id, query)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str, contact: ContactUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a contact"""
    updated = await ContactService.update_contact(db, contact_id, contact)
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated


@router.delete("/{contact_id}", status_code=204)
async def delete_contact(contact_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a contact"""
    success = await ContactService.delete_contact(db, contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.get("/user/{user_id}/favorites", response_model=List[ContactResponse])
async def get_favorite_contacts(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get favorite contacts"""
    return await ContactService.get_favorites(db, user_id)


@router.post("/{contact_id}/mark-contacted", response_model=ContactResponse)
async def mark_contacted(contact_id: str, db: AsyncSession = Depends(get_db)):
    """Update last contacted timestamp"""
    contact = await ContactService.update_last_contacted(db, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact
