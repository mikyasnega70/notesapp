from .database import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy_utils import EmailType


class Users(Base):
    __tablename__='users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(EmailType, unique=True)
    name = Column(String(20))
    hashed_password = Column(String)
    role = Column(String)

class Notes(Base):
    __tablename__='notes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))

    
