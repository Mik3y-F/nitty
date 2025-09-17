import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.events.models import Event, EventCreate, EventUpdate

logger = logging.getLogger(__name__)


def create_event(
    *, session: Session, event_create: EventCreate, created_by: UUID
) -> Event:
    """Create a new event."""
    db_obj = Event.model_validate(event_create, update={"created_by": created_by})
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    logger.info(f"Created event: {db_obj.id}")
    return db_obj


def get_event(*, session: Session, event_id: UUID) -> Optional[Event]:
    """Get an event by ID."""
    statement = select(Event).where(Event.id == event_id)
    event = session.exec(statement).first()
    logger.info(f"Retrieved event: {event}")
    return event


def get_events(
    *,
    session: Session,
    skip: int = 0,
    limit: int = 100,
    community_id: Optional[UUID] = None,
    is_public: Optional[bool] = None,
    is_active: Optional[bool] = None,
    upcoming_only: bool = False,
) -> List[Event]:
    """Get events with optional filtering."""
    statement = select(Event)

    if community_id is not None:
        statement = statement.where(Event.community_id == community_id)

    if is_public is not None:
        statement = statement.where(Event.is_public == is_public)

    if is_active is not None:
        statement = statement.where(Event.is_active == is_active)

    if upcoming_only:
        statement = statement.where(Event.start_time >= datetime.now())

    statement = statement.order_by(Event.start_time).offset(skip).limit(limit)
    events = session.exec(statement).all()
    logger.info(f"Retrieved {len(events)} events")
    return events


def get_events_by_creator(
    *, session: Session, created_by: UUID, skip: int = 0, limit: int = 100
) -> List[Event]:
    """Get events created by a specific user."""
    statement = select(Event).where(Event.created_by == created_by)
    statement = statement.order_by(Event.start_time).offset(skip).limit(limit)
    events = session.exec(statement).all()
    logger.info(f"Retrieved {len(events)} events for user {created_by}")
    return events


def get_events_by_community(
    *, session: Session, community_id: UUID, skip: int = 0, limit: int = 100
) -> List[Event]:
    """Get events for a specific community."""
    statement = select(Event).where(Event.community_id == community_id)
    statement = statement.order_by(Event.start_time).offset(skip).limit(limit)
    events = session.exec(statement).all()
    logger.info(f"Retrieved {len(events)} events for community {community_id}")
    return events


def update_event(*, session: Session, db_event: Event, event_in: EventUpdate) -> Event:
    """Update an event."""
    event_data = event_in.model_dump(exclude_unset=True)
    event_data["updated_at"] = datetime.now()

    db_event.sqlmodel_update(event_data)
    session.add(db_event)
    session.commit()
    session.refresh(db_event)
    logger.info(f"Updated event: {db_event.id}")
    return db_event


def delete_event(*, session: Session, event_id: UUID) -> bool:
    """Delete an event (soft delete by setting is_active=False)."""
    event = get_event(session=session, event_id=event_id)
    if not event:
        return False

    event.is_active = False
    event.updated_at = datetime.now()
    session.add(event)
    session.commit()
    logger.info(f"Soft deleted event: {event_id}")
    return True


def hard_delete_event(*, session: Session, event_id: UUID) -> bool:
    """Permanently delete an event from the database."""
    event = get_event(session=session, event_id=event_id)
    if not event:
        return False

    session.delete(event)
    session.commit()
    logger.info(f"Hard deleted event: {event_id}")
    return True


def search_events(
    *, session: Session, query: str, skip: int = 0, limit: int = 100
) -> List[Event]:
    """Search events by title or description."""
    statement = select(Event).where(
        (Event.title.ilike(f"%{query}%"))
        | (Event.description.ilike(f"%{query}%"))
        | (Event.location.ilike(f"%{query}%"))
    )
    statement = statement.order_by(Event.start_time).offset(skip).limit(limit)
    events = session.exec(statement).all()
    logger.info(f"Found {len(events)} events matching query: {query}")
    return events


def get_upcoming_events(
    *, session: Session, skip: int = 0, limit: int = 100
) -> List[Event]:
    """Get upcoming events (start_time >= now)."""
    statement = select(Event).where(Event.start_time >= datetime.now())
    statement = statement.order_by(Event.start_time).offset(skip).limit(limit)
    events = session.exec(statement).all()
    logger.info(f"Retrieved {len(events)} upcoming events")
    return events


def get_events_by_date_range(
    *,
    session: Session,
    start_date: datetime,
    end_date: datetime,
    skip: int = 0,
    limit: int = 100,
) -> List[Event]:
    """Get events within a specific date range."""
    statement = select(Event).where(
        Event.start_time >= start_date, Event.start_time <= end_date
    )
    statement = statement.order_by(Event.start_time).offset(skip).limit(limit)
    events = session.exec(statement).all()
    logger.info(f"Retrieved {len(events)} events between {start_date} and {end_date}")
    return events
