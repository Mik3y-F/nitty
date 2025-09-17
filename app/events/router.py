import logging
from datetime import datetime
from typing import Annotated, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

import app.events.service as event_service
from app.auth.models import User
from app.communities.service import get_community
from app.database import DbSession
from app.deps import get_current_user
from app.events.models import EventCreate, EventPublic, EventUpdate

logger = logging.getLogger(__name__)

events_router = APIRouter(tags=["events"])


@events_router.post("/", response_model=EventPublic)
def create_event(
    session: DbSession,
    event_in: EventCreate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """Create a new event."""
    # Verify the community exists and user has access
    community = get_community(session=session, community_id=event_in.community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    # Check if user is the creator of the community or has permission
    if community.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to create events in this community",
        )

    event = event_service.create_event(
        session=session, event_create=event_in, created_by=current_user.id
    )
    return event


@events_router.get("/", response_model=List[EventPublic])
def get_events(
    session: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    community_id: Optional[UUID] = Query(None),
    is_public: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    upcoming_only: bool = Query(False),
) -> Any:
    """Get events with optional filtering."""
    events = event_service.get_events(
        session=session,
        skip=skip,
        limit=limit,
        community_id=community_id,
        is_public=is_public,
        is_active=is_active,
        upcoming_only=upcoming_only,
    )
    return events


@events_router.get("/search", response_model=List[EventPublic])
def search_events(
    session: DbSession,
    q: str = Query(..., min_length=1, max_length=100),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Search events by title, description, or location."""
    events = event_service.search_events(
        session=session, query=q, skip=skip, limit=limit
    )
    return events


@events_router.get("/upcoming", response_model=List[EventPublic])
def get_upcoming_events(
    session: DbSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Get upcoming events."""
    events = event_service.get_upcoming_events(session=session, skip=skip, limit=limit)
    return events


@events_router.get("/my", response_model=List[EventPublic])
def get_my_events(
    session: DbSession,
    current_user: Annotated[User, Depends(get_current_user)],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Get events created by the current user."""
    events = event_service.get_events_by_creator(
        session=session, created_by=current_user.id, skip=skip, limit=limit
    )
    return events


@events_router.get("/community/{community_id}", response_model=List[EventPublic])
def get_community_events(
    session: DbSession,
    community_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Get events for a specific community."""
    # Verify the community exists
    community = get_community(session=session, community_id=community_id)
    if not community:
        raise HTTPException(status_code=404, detail="Community not found")

    events = event_service.get_events_by_community(
        session=session, community_id=community_id, skip=skip, limit=limit
    )
    return events


@events_router.get("/date-range", response_model=List[EventPublic])
def get_events_by_date_range(
    session: DbSession,
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Get events within a specific date range."""
    if start_date >= end_date:
        raise HTTPException(
            status_code=400, detail="Start date must be before end date"
        )

    events = event_service.get_events_by_date_range(
        session=session,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    return events


@events_router.get("/{event_id}", response_model=EventPublic)
def get_event(
    session: DbSession,
    event_id: UUID,
) -> Any:
    """Get a specific event by ID."""
    event = event_service.get_event(session=session, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@events_router.put("/{event_id}", response_model=EventPublic)
def update_event(
    session: DbSession,
    event_id: UUID,
    event_in: EventUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """Update an event."""
    event = event_service.get_event(session=session, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is the creator
    if event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    event = event_service.update_event(
        session=session, db_event=event, event_in=event_in
    )
    return event


@events_router.delete("/{event_id}")
def delete_event(
    session: DbSession,
    event_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """Delete an event (soft delete)."""
    event = event_service.get_event(session=session, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is the creator
    if event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = event_service.delete_event(session=session, event_id=event_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete event")

    return {"message": "Event deleted successfully"}


@events_router.delete("/{event_id}/permanent")
def permanently_delete_event(
    session: DbSession,
    event_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> Any:
    """Permanently delete an event from the database."""
    event = event_service.get_event(session=session, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if user is the creator
    if event.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = event_service.hard_delete_event(session=session, event_id=event_id)
    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to permanently delete event"
        )

    return {"message": "Event permanently deleted"}
