from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base # Import Base from models.py

# SQLite database URL for development
DATABASE_URL = "sqlite:///./test_app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
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
