from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, User
from auth_utils import get_password_hash # Import from auth_utils
from datetime import datetime

def create_initial_users(db: Session):
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # Check if users already exist to avoid duplicates
    if db.query(User).filter(User.username == "student1").first():
        print("Test users already exist. Skipping creation.")
        return

    # Create test users
    student1_password = get_password_hash("password123")
    tutor1_password = get_password_hash("adminpass")

    student1 = User(username="student1", hashed_password=student1_password, role="student")
    tutor1 = User(username="tutor1", hashed_password=tutor1_password, role="tutor")
    
    db.add(student1)
    db.add(tutor1)
    db.commit()
    db.refresh(student1)
    db.refresh(tutor1)

    print("Test users created:")
    print(f"- Student: {student1.username} (ID: {student1.id}, Role: {student1.role})")
    print(f"- Tutor: {tutor1.username} (ID: {tutor1.id}, Role: {tutor1.role})")

if __name__ == "__main__":
    print("Seeding database with initial users...")
    db = SessionLocal()
    try:
        create_initial_users(db)
    finally:
        db.close()
    print("Database seeding complete.")
