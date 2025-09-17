import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship

from app.database import NittySQLModel

if TYPE_CHECKING:
    from app.auth.models import User


class CommunityBase(NittySQLModel):
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    is_public: bool = Field(default=True)
    is_active: bool = Field(default=True)


class CommunityCreate(CommunityBase):
    pass


class CommunityUpdate(NittySQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    is_public: Optional[bool] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class Community(CommunityBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: uuid.UUID = Field(foreign_key="user.id")

    # Relationships
    creator: "User" = Relationship(back_populates="created_communities")


class CommunityPublic(CommunityBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    created_by: uuid.UUID


# Rebuild models to resolve forward references
Community.model_rebuild()
