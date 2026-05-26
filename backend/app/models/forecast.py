from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    model_type = Column(String(50), nullable=False)  # linear_regression, prophet
    periods = Column(Integer, nullable=False)
    accuracy_score = Column(Float, nullable=True)
    mae = Column(Float, nullable=True)
    rmse = Column(Float, nullable=True)
    predictions = Column(JSON, nullable=True)
    historical_data = Column(JSON, nullable=True)
    feature_columns = Column(JSON, nullable=True)
    target_column = Column(String(100), nullable=True)
    date_column = Column(String(100), nullable=True)
    status = Column(String(50), default="pending")  # pending, running, completed, error
    error_message = Column(Text, nullable=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="forecasts")
    dataset = relationship("Dataset", back_populates="forecasts")
