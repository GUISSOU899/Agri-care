# Backend/app/models/forecast.py
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base  # ✅ (au lieu de app.db.session)

class Forecast(Base):
    __tablename__ = "forecast"

    id = Column(Integer, primary_key=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id"), nullable=False)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)

    date = Column(Date, nullable=False)
    horizon_days = Column(Integer, nullable=False)
    yield_index = Column(Float, nullable=False)

    temperature_c = Column(Float, nullable=True)
    tmin_c = Column(Float, nullable=True)
    tmax_c = Column(Float, nullable=True)
    tmean_c = Column(Float, nullable=True)
    rainfall_mm = Column(Float, nullable=True)
    evapotranspiration_mm = Column(Float, nullable=True)

    source = Column(String(30), nullable=False, server_default="api")
    fetched_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    model_version = Column(String(30), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("region_id", "crop_id", "date", name="uix_forecast_region_crop_date"),
    )

    region = relationship("Region", back_populates="forecasts")
    crop = relationship("Crop", back_populates="forecasts")
