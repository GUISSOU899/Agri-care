import sys
import os

# Add the parent directory to sys.path to resolve imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash

def create_admin_user():
    db: Session = SessionLocal()
    try:
        email = "admin@agricare.com"
        password = "admin"
        
        # Check if exists
        user = db.query(User).filter(User.email == email).first()
        if user:
            print(f"User {email} already exists.")
            if user.role != "admin":
                print("Promoting to admin...")
                user.role = "admin"
                db.commit()
                print("Done.")
            return

        print(f"Creating admin user: {email} / {password}")
        db_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            role="admin",
            is_active=True
        )
        db.add(db_user)
        db.commit()
        print("Admin user created successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
