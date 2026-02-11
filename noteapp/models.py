from .database import Base
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func

class Notes(Base):
    __tablename__='notes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)

    
