from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime, String, UniqueConstraint, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base
from sqlalchemy.orm import relationship

class YieldObserved(Base):
    __tablename__ = "yield_observed"
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)
    season_year = Column(Integer, nullable=False)
    yield_t_ha = Column(Float, nullable=False)
    source = Column(String(50), nullable=False) # e.g., "ground_truth", "survey"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    region = relationship("Region")
    crop = relationship("Crop")

    __table_args__ = (
        UniqueConstraint('region_id', 'crop_id', 'season_year', name='uix_yield_observed_region_crop_year'),
    )

class NDVITimeseries(Base):
    __tablename__ = "ndvi_timeseries"
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)
    date = Column(Date, nullable=False)
    ndvi = Column(Float, nullable=False)
    source = Column(String(50), nullable=False) # e.g., "sentinel-2", "mock"
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    region = relationship("Region")
    crop = relationship("Crop")

class SeasonCalendar(Base):
    __tablename__ = "season_calendar"
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)
    season_year = Column(Integer, nullable=False)
    sowing_date = Column(Date, nullable=False)
    harvest_date = Column(Date, nullable=True)
    notes = Column(String(200), nullable=True)

    region = relationship("Region")
    crop = relationship("Crop")

    __table_args__ = (
        UniqueConstraint('region_id', 'crop_id', 'season_year', name='uix_season_calendar_region_crop_year'),
    )

class AquaCropSim(Base):
    __tablename__ = "aquacrop_sim"
    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)
    season_year = Column(Integer, nullable=False)
    simulated_yield_t_ha = Column(Float, nullable=False)
    params_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    region = relationship("Region")
    crop = relationship("Crop")

    __table_args__ = (
        UniqueConstraint('region_id', 'crop_id', 'season_year', name='uix_aquacrop_sim_region_crop_year'),
    )
