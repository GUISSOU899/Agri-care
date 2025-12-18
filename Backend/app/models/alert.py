from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Alert(Base):
    __tablename__ = "alert"
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=True)
    alert_type = Column(String(50), nullable=False)  # irrigation, yield, etc.
    message = Column(Text, nullable=False)
    severity = Column(String(20), default="info")  # info, warning, critical
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    region = relationship("Region", back_populates="alerts")
    crop = relationship("Crop", back_populates="alerts")
