import uuid
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship

from app.database import NittySQLModel

if TYPE_CHECKING:
    from app.communities.models import Community
    from app.events.models import Event


class UserBase(NittySQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(NittySQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

    # Relationships
    created_communities: list["Community"] = Relationship(back_populates="creator")
    created_events: list["Event"] = Relationship(back_populates="creator")


class UserPublic(UserBase):
    id: uuid.UUID


class Token(NittySQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(NittySQLModel):
    sub: str | None = None


# Rebuild models to resolve forward references
User.model_rebuild()
