"""
One-off script to create (or promote) an admin user.
Usage:
    python -m scripts.create_admin admin@example.com "Admin User" "StrongPass123!"
"""
import sys

sys.path.append(".")

from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole


def main():
    if len(sys.argv) != 4:
        print("Usage: python -m scripts.create_admin <email> <full_name> <password>")
        sys.exit(1)
    email, full_name, password = sys.argv[1], sys.argv[2], sys.argv[3]

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = UserRole.ADMIN
            user.is_active = True
            print(f"Existing user {email} promoted to admin.")
        else:
            user = User(full_name=full_name, email=email, hashed_password=hash_password(password),
                        role=UserRole.ADMIN)
            db.add(user)
            print(f"Created new admin user {email}.")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
