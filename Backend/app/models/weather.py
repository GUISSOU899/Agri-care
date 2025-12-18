from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class WeatherDaily(Base):
    __tablename__ = "weather_daily"
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    date = Column(Date, nullable=False)
    tmin = Column(Float)
    tmax = Column(Float)
    tavg = Column(Float)
    precipitation = Column(Float)
    region = relationship("Region", back_populates="weather")
