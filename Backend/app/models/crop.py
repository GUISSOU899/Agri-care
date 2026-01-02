from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Crop(Base):
    __tablename__ = "crop"  # Changed from "crops" to match ForeignKey("crop.id") in Forecast
    __table_args__ = (UniqueConstraint("name", name="uq_crop_name"),)

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False)
    variety = Column(String(100), nullable=True)
    water_need = Column(Float, nullable=False)  # mm per day
    temp_low = Column(Float, nullable=False)   # °C
    temp_high = Column(Float, nullable=False)  # °C
    rain_threshold = Column(Float, nullable=False)  # mm deficit threshold
    
    forecasts = relationship("Forecast", back_populates="crop")
    alerts = relationship("Alert", back_populates="crop", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Crop id={self.id} name={self.name}>"
