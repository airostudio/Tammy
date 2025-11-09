"""Visitor API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.schemas.visitor import VisitorCreate, VisitorUpdate, VisitorResponse
from app.services.visitor_service import VisitorService

router = APIRouter()


@router.post("/", response_model=VisitorResponse, status_code=201)
async def create_visitor(visitor: VisitorCreate, db: AsyncSession = Depends(get_db)):
    """Create a new visitor record"""
    return await VisitorService.create_visitor(db, visitor)


@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(visitor_id: str, db: AsyncSession = Depends(get_db)):
    """Get a visitor by ID"""
    visitor = await VisitorService.get_visitor(db, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor


@router.get("/", response_model=List[VisitorResponse])
async def get_visitors(
    status: Optional[str] = None,
    visit_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get all visitors"""
    return await VisitorService.get_all_visitors(db, status, visit_type)


@router.put("/{visitor_id}", response_model=VisitorResponse)
async def update_visitor(
    visitor_id: str, visitor: VisitorUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a visitor record"""
    updated = await VisitorService.update_visitor(db, visitor_id, visitor)
    if not updated:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return updated


@router.delete("/{visitor_id}", status_code=204)
async def delete_visitor(visitor_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a visitor record"""
    success = await VisitorService.delete_visitor(db, visitor_id)
    if not success:
        raise HTTPException(status_code=404, detail="Visitor not found")


@router.post("/{visitor_id}/check-in", response_model=VisitorResponse)
async def check_in_visitor(
    visitor_id: str, badge_number: Optional[str] = None, db: AsyncSession = Depends(get_db)
):
    """Check in a visitor"""
    visitor = await VisitorService.check_in_visitor(db, visitor_id, badge_number)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor


@router.post("/{visitor_id}/check-out", response_model=VisitorResponse)
async def check_out_visitor(visitor_id: str, db: AsyncSession = Depends(get_db)):
    """Check out a visitor"""
    visitor = await VisitorService.check_out_visitor(db, visitor_id)
    if not visitor:
        raise HTTPException(status_code=404, detail="Visitor not found")
    return visitor


@router.get("/current/all", response_model=List[VisitorResponse])
async def get_current_visitors(db: AsyncSession = Depends(get_db)):
    """Get all currently checked-in visitors"""
    return await VisitorService.get_current_visitors(db)


@router.get("/scheduled/upcoming", response_model=List[VisitorResponse])
async def get_scheduled_visitors(hours: int = 24, db: AsyncSession = Depends(get_db)):
    """Get scheduled visitors"""
    return await VisitorService.get_scheduled_visitors(db, hours)


@router.get("/host/{host_name}", response_model=List[VisitorResponse])
async def get_visitors_by_host(host_name: str, db: AsyncSession = Depends(get_db)):
    """Get visitors for a specific host"""
    return await VisitorService.get_visitors_by_host(db, host_name)
