"""Security and Authentication utilities."""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from app.core.config import get_settings

settings = get_settings()

# We configure pwdlib to use argon2
password_hash = PasswordHash((Argon2Hasher(),))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against the stored hash."""
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate a secure hash from a plain password."""
    return password_hash.hash(password)


def create_access_token(subject: str | Any, expires_delta: timedelta | None = None) -> str:
    """Create a signed JWT access token.
    
    Args:
        subject: The user ID or unique subject identifier.
        expires_delta: Optional custom expiration timedelta.
    """
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
        
    to_encode = {"exp": expire, "sub": str(subject)}
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.jwt_secret_key, 
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT access token.
    
    Raises:
        jwt.InvalidTokenError: If the token is invalid, expired, or malformed.
    """
    return jwt.decode(
        token, 
        settings.jwt_secret_key, 
        algorithms=[settings.jwt_algorithm]
    )
