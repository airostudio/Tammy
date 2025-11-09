"""Message API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.schemas.message import MessageCreate, MessageUpdate, MessageResponse
from app.services.message_service import MessageService

router = APIRouter()


@router.post("/", response_model=MessageResponse, status_code=201)
async def create_message(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    """Create a new message"""
    return await MessageService.create_message(db, message)


@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(message_id: str, db: AsyncSession = Depends(get_db)):
    """Get a message by ID (marks as read)"""
    message = await MessageService.get_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.get("/", response_model=List[MessageResponse])
async def get_messages(
    message_type: Optional[str] = None,
    status: Optional[str] = None,
    direction: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get messages with optional filtering"""
    return await MessageService.get_messages(db, message_type, status, direction)


@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: str, message: MessageUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a message"""
    updated = await MessageService.update_message(db, message_id, message)
    if not updated:
        raise HTTPException(status_code=404, detail="Message not found")
    return updated


@router.delete("/{message_id}", status_code=204)
async def delete_message(message_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a message"""
    success = await MessageService.delete_message(db, message_id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found")


@router.get("/unread/all", response_model=List[MessageResponse])
async def get_unread_messages(db: AsyncSession = Depends(get_db)):
    """Get all unread messages"""
    return await MessageService.get_unread_messages(db)


@router.get("/flagged/all", response_model=List[MessageResponse])
async def get_flagged_messages(db: AsyncSession = Depends(get_db)):
    """Get all flagged messages"""
    return await MessageService.get_flagged_messages(db)


@router.get("/search/", response_model=List[MessageResponse])
async def search_messages(query: str, db: AsyncSession = Depends(get_db)):
    """Search messages"""
    return await MessageService.search_messages(db, query)


@router.post("/{message_id}/read", response_model=MessageResponse)
async def mark_as_read(message_id: str, db: AsyncSession = Depends(get_db)):
    """Mark a message as read"""
    message = await MessageService.mark_as_read(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message


@router.post("/{message_id}/archive", response_model=MessageResponse)
async def archive_message(message_id: str, db: AsyncSession = Depends(get_db)):
    """Archive a message"""
    message = await MessageService.archive_message(db, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message
