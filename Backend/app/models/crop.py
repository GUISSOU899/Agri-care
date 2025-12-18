from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.session import Base

class Crop(Base):
    __tablename__ = "crop"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(20), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    
    forecasts = relationship("Forecast", back_populates="crop", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="crop", cascade="all, delete-orphan")
