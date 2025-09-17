import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.database import NittySQLModel

if TYPE_CHECKING:
    from app.auth.models import User, UserPublic
    from app.communities.models import Community, CommunityPublic


class EventBase(NittySQLModel):
    title: str = Field(max_length=200, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    start_time: datetime
    end_time: Optional[datetime] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=200)
    is_online: bool = Field(default=False)
    max_attendees: Optional[int] = Field(default=None, ge=1)
    is_active: bool = Field(default=True)
    is_public: bool = Field(default=True)


class EventCreate(EventBase):
    community_id: uuid.UUID


class EventUpdate(NittySQLModel):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    start_time: Optional[datetime] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    location: Optional[str] = Field(default=None, max_length=200)
    is_online: Optional[bool] = Field(default=None)
    max_attendees: Optional[int] = Field(default=None, ge=1)
    is_active: Optional[bool] = Field(default=None)
    is_public: Optional[bool] = Field(default=None)


class Event(EventBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: uuid.UUID = Field(foreign_key="user.id")
    community_id: uuid.UUID = Field(foreign_key="community.id")

    # Relationships
    creator: "User" = Relationship(back_populates="created_events")
    community: "Community" = Relationship(back_populates="events")


class EventPublic(EventBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID
    community_id: uuid.UUID


class EventWithDetails(EventPublic):
    creator: "UserPublic"
    community: "CommunityPublic"


# Rebuild models to resolve forward references
Event.model_rebuild()
