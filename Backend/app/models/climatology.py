from sqlalchemy import Column, Integer, Float, ForeignKey, UniqueConstraint
from app.db.base_class import Base

class ClimatologyDaily(Base):
    __tablename__ = "climatology_daily"
    
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False, index=True)
    day_of_year = Column(Integer, nullable=False, index=True)
    
    tmin_c = Column(Float, nullable=True)
    tmax_c = Column(Float, nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    
    std_t = Column(Float, nullable=True) # Standard deviation for temp
    std_r = Column(Float, nullable=True) # Standard deviation for rain

    __table_args__ = (
        UniqueConstraint('region_id', 'day_of_year', name='uix_climatology_region_doy'),
    )
