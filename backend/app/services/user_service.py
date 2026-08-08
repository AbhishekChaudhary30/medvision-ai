"""User management service."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user_create: UserCreate) -> User | None:
    """Create a new user. Returns None if email already exists."""
    hashed_password = get_password_hash(user_create.password)
    
    db_user = User(
        email=user_create.email,
        password_hash=hashed_password,
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        return None


def get_user_by_email(db: Session, email: str) -> User | None:
    """Retrieve a user by email."""
    return db.query(User).filter(User.email == email).first()


def update_user(db: Session, user: User, update_data: UserUpdate) -> User:
    """Update user fields."""
    if update_data.role is not None:
        user.role = update_data.role
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
        
    db.commit()
    db.refresh(user)
    return user
