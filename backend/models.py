from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class MasterImage(Base):
    __tablename__ = "master_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    path = Column(String)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String)

    variants = relationship("Variant", back_populates="master", cascade="all, delete-orphan")

class Variant(Base):
    __tablename__ = "variants"

    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("master_images.id"))
    filename = Column(String, index=True)
    path = Column(String)
    variant_type = Column(String)
    aspect_ratio = Column(String)
    palette = Column(String, nullable=True)
    similarity_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    master = relationship("MasterImage", back_populates="variants")
