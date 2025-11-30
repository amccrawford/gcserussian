from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base # Import Base from models.py
import os
from dotenv import load_dotenv

load_dotenv()

# Get DATABASE_URL from environment, defaulting to local SQLite for dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test_app.db")

# Handle potential "postgres://" legacy prefix (SQLAlchemy requires "postgresql://")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configure connect_args only for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Database and tables created/updated via database.py.")
