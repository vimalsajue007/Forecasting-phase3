"""
Anomaly Detection routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.anomaly import AnomalyDetection
from app.core.security import get_current_user
from app.core.roles import require_permission
from app.ml.anomaly import detect_anomalies

router = APIRouter(prefix="/api/anomalies", tags=["Anomaly Detection"])


class AnomalyRequest(BaseModel):
    dataset_id: int
    date_column: str
    target_column: str
    sensitivity: float = 1.5


class AnomalyResponse(BaseModel):
    id: int
    dataset_id: int
    target_column: str
    anomaly_count: int
    severity: str
    summary: str
    created_at: datetime
    model_config = {"from_attributes": True}


@router.post("/detect", response_model=AnomalyResponse)
def detect(
    request: AnomalyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("detect_anomalies")),
):
    dataset = db.query(Dataset).filter(
        Dataset.id == request.dataset_id, Dataset.owner_id == current_user.id
    ).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if dataset.status != "processed":
        raise HTTPException(status_code=400, detail="Dataset not processed")

    try:
        result = detect_anomalies(
            dataset.file_path,
            request.date_column,
            request.target_column,
            request.sensitivity,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    record = AnomalyDetection(
        dataset_id=dataset.id,
        owner_id=current_user.id,
        target_column=request.target_column,
        date_column=request.date_column,
        anomalies=result["anomalies"],
        anomaly_count=result["anomaly_count"],
        severity=result["severity"],
        summary=result["summary"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        **AnomalyResponse.model_validate(record).model_dump(),
        "anomalies": result["anomalies"],
        "statistics": result["statistics"],
        "seasonal_insights": result["seasonal_insights"],
    }


@router.get("/", response_model=List[AnomalyResponse])
def list_anomalies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return db.query(AnomalyDetection).filter(
        AnomalyDetection.owner_id == current_user.id
    ).order_by(AnomalyDetection.created_at.desc()).all()


@router.get("/{anomaly_id}")
def get_anomaly(
    anomaly_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = db.query(AnomalyDetection).filter(
        AnomalyDetection.id == anomaly_id,
        AnomalyDetection.owner_id == current_user.id,
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": record.id,
        "dataset_id": record.dataset_id,
        "target_column": record.target_column,
        "anomaly_count": record.anomaly_count,
        "severity": record.severity,
        "summary": record.summary,
        "anomalies": record.anomalies,
        "created_at": str(record.created_at),
    }
