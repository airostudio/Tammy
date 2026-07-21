"""Contact service for relationship management"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime
from typing import List, Optional
import uuid

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactService:
    """Service for managing contacts and relationships"""

    @staticmethod
    async def create_contact(db: AsyncSession, contact: ContactCreate) -> Contact:
        """Create a new contact"""
        full_name = f"{contact.first_name} {contact.last_name}"

        db_contact = Contact(
            id=str(uuid.uuid4()),
            user_id=contact.user_id,
            first_name=contact.first_name,
            last_name=contact.last_name,
            full_name=full_name,
            email=contact.email,
            phone_number=contact.phone_number,
            mobile_number=contact.mobile_number,
            company=contact.company,
            job_title=contact.job_title,
            department=contact.department,
            birthday=contact.birthday,
            anniversary=contact.anniversary,
            relationship_type=contact.relationship_type,
            priority=contact.priority,
            notes=contact.notes,
            tags=contact.tags,
        )

        db.add(db_contact)
        await db.commit()
        await db.refresh(db_contact)
        return db_contact

    @staticmethod
    async def get_contact(db: AsyncSession, contact_id: str) -> Optional[Contact]:
        """Get a contact by ID"""
        result = await db.execute(select(Contact).where(Contact.id == contact_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_contacts(db: AsyncSession, user_id: Optional[str] = None) -> List[Contact]:
        """Get contacts, optionally filtered by user.
        Omitting user_id returns contacts across all users (admin use)."""
        query = select(Contact)
        if user_id:
            query = query.where(Contact.user_id == user_id)
        result = await db.execute(query.order_by(Contact.full_name))
        return list(result.scalars().all())

    @staticmethod
    async def search_contacts(db: AsyncSession, user_id: str, query: str) -> List[Contact]:
        """Search contacts by name, email, or company"""
        search_query = select(Contact).where(
            Contact.user_id == user_id,
            or_(
                Contact.full_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
                Contact.company.ilike(f"%{query}%"),
            ),
        )

        result = await db.execute(search_query)
        return list(result.scalars().all())

    @staticmethod
    async def update_contact(
        db: AsyncSession, contact_id: str, contact_update: ContactUpdate
    ) -> Optional[Contact]:
        """Update a contact"""
        db_contact = await ContactService.get_contact(db, contact_id)
        if not db_contact:
            return None

        update_data = contact_update.model_dump(exclude_unset=True)

        # Update full_name if first_name or last_name changed
        if "first_name" in update_data or "last_name" in update_data:
            first_name = update_data.get("first_name", db_contact.first_name)
            last_name = update_data.get("last_name", db_contact.last_name)
            update_data["full_name"] = f"{first_name} {last_name}"

        for field, value in update_data.items():
            setattr(db_contact, field, value)

        await db.commit()
        await db.refresh(db_contact)
        return db_contact

    @staticmethod
    async def delete_contact(db: AsyncSession, contact_id: str) -> bool:
        """Delete a contact"""
        db_contact = await ContactService.get_contact(db, contact_id)
        if not db_contact:
            return False

        await db.delete(db_contact)
        await db.commit()
        return True

    @staticmethod
    async def get_favorites(db: AsyncSession, user_id: str) -> List[Contact]:
        """Get favorite contacts"""
        result = await db.execute(
            select(Contact)
            .where(Contact.user_id == user_id, Contact.is_favorite == True)
            .order_by(Contact.full_name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_last_contacted(db: AsyncSession, contact_id: str) -> Optional[Contact]:
        """Update the last contacted timestamp"""
        db_contact = await ContactService.get_contact(db, contact_id)
        if not db_contact:
            return None

        db_contact.last_contacted = datetime.utcnow()
        await db.commit()
        await db.refresh(db_contact)
        return db_contact

    @staticmethod
    async def get_contacts_by_company(db: AsyncSession, user_id: str, company: str) -> List[Contact]:
        """Get all contacts from a specific company"""
        result = await db.execute(
            select(Contact).where(Contact.user_id == user_id, Contact.company == company)
        )
        return list(result.scalars().all())
