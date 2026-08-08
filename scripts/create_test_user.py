# Add backend and root to path
import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(project_root, "backend"))
sys.path.insert(0, project_root)

from app.db.session import SessionLocal  # noqa: E402
from app.models.user import UserRole  # noqa: E402
from app.schemas.user import UserCreate  # noqa: E402
from app.services.user_service import create_user  # noqa: E402


def main():
    db = SessionLocal()
    try:
        user_data = UserCreate(email="admin@example.com", password="password123", role=UserRole.ADMIN)
        user = create_user(db, user_data)
        if user:
            print("User created successfully!")
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
        else:
            print("Failed to create user (might already exist).")
    finally:
        db.close()


if __name__ == "__main__":
    main()
