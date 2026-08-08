"""Admin endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import require_role
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import update_user

router = APIRouter()


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_role([UserRole.ADMIN]))],
    skip: int = 0,
    limit: int = 100,
):
    """Retrieve all users (admin only)."""
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_role([UserRole.ADMIN]))],
):
    """Retrieve a specific user by ID (admin only)."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/users/{user_id}", response_model=UserResponse)
def patch_user(
    user_id: UUID,
    update_data: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_admin: Annotated[User, Depends(require_role([UserRole.ADMIN]))],
):
    """Update a user's role or status (admin only)."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return update_user(db, user, update_data)
