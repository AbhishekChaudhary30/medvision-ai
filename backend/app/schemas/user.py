"""User schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Base user attributes."""

    email: EmailStr


class UserCreate(UserBase):
    """Properties to receive on user creation."""

    password: str = Field(min_length=8, description="Password must be at least 8 characters long")


class UserUpdate(BaseModel):
    """Properties to receive on user update."""

    role: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """Properties to return to client."""

    id: UUID
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    """JWT Token schema."""

    access_token: str
    token_type: str = "bearer"
