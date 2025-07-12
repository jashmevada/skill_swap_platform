from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime

SQLITE_DATABASE_URL = "sqlite:///skill_swap.db"

engine = create_engine(
    SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Association table for user skills (many-to-many)
user_skills_offered = Table(
    'user_skills_offered',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

user_skills_wanted = Table(
    'user_skills_wanted', 
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    location = Column(String)
    profile_photo = Column(String)  # URL or file path
    bio = Column(Text)
    availability = Column(String)  # JSON string for flexibility
    is_public = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    skills_offered = relationship("Skill", secondary=user_skills_offered, back_populates="users_offering")
    skills_wanted = relationship("Skill", secondary=user_skills_wanted, back_populates="users_wanting")
    
    sent_requests = relationship("SwapRequest", foreign_keys="SwapRequest.requester_id", back_populates="requester")
    received_requests = relationship("SwapRequest", foreign_keys="SwapRequest.requested_id", back_populates="requested")
    
    given_feedback = relationship("Feedback", foreign_keys="Feedback.giver_id", back_populates="giver")
    received_feedback = relationship("Feedback", foreign_keys="Feedback.receiver_id", back_populates="receiver")


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, index=True)
    description = Column(Text)
    is_approved = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    users_offering = relationship("User", secondary=user_skills_offered, back_populates="skills_offered")
    users_wanting = relationship("User", secondary=user_skills_wanted, back_populates="skills_wanted")


class SwapRequest(Base):
    __tablename__ = "swap_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_offered_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    skill_wanted_id = Column(Integer, ForeignKey("skills.id"), nullable=False)
    message = Column(Text)
    status = Column(String, default="pending")  # pending, accepted, rejected, completed, cancelled
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="sent_requests")
    requested = relationship("User", foreign_keys=[requested_id], back_populates="received_requests")
    skill_offered = relationship("Skill", foreign_keys=[skill_offered_id])
    skill_wanted = relationship("Skill", foreign_keys=[skill_wanted_id])


class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    swap_request_id = Column(Integer, ForeignKey("swap_requests.id"), nullable=False)
    giver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    swap_request = relationship("SwapRequest")
    giver = relationship("User", foreign_keys=[giver_id], back_populates="given_feedback")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_feedback")


class AdminMessage(Base):
    __tablename__ = "admin_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
