from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class YieldHistory(Base):
    __tablename__ = "yield_history"
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    crop = Column(String(50), nullable=False)
    year = Column(Integer, nullable=False)
    date_harvest = Column(Date, nullable=False)
    yield_value = Column(Float, nullable=False)
    yield_index = Column(Float, nullable=False)  # 0-1 normalized
    
    region = relationship("Region", back_populates="yields")
