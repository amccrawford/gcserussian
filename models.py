from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="student") # e.g., "student", "admin"

    sessions = relationship("Session", back_populates="user")

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    theme = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    subtopic = Column(String)
    difficulty = Column(String, nullable=False)
    language = Column(String, default="Russian")

    user = relationship("User", back_populates="sessions")
    results = relationship("Result", back_populates="session")

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    original_question = Column(Text, nullable=False)
    question_english_translation = Column(Text, nullable=False)
    student_transcription = Column(Text, nullable=False)
    student_translation = Column(Text, nullable=False)
    score = Column(Integer, nullable=False) # Score out of 10
    feedback_json = Column(JSON, nullable=False) # Store LLM feedback as JSON

    session = relationship("Session", back_populates="results")
