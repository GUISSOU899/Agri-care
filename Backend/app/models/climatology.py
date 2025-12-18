from sqlalchemy import Column, Integer, Float
from app.db.session import Base

class ClimatologyDaily(Base):
    __tablename__ = "climatology_daily"
    
    region_id = Column(Integer, primary_key=True, index=True)
    day_of_year = Column(Integer, primary_key=True, index=True)
    
    tmin_c = Column(Float, nullable=True)
    tmax_c = Column(Float, nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    
    std_t = Column(Float, nullable=True) # Standard deviation for temp
    std_r = Column(Float, nullable=True) # Standard deviation for rain
