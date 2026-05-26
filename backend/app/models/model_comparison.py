from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base


class ModelComparison(Base):
    __tablename__ = "model_comparisons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    periods = Column(Integer, nullable=False)
    target_column = Column(String(100), nullable=False)
    date_column = Column(String(100), nullable=False)
    results = Column(JSON, nullable=True)  # comparison results for all models
    best_model = Column(String(50), nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User")
    dataset = relationship("Dataset")
