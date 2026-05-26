import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.schemas.forecast import DatasetResponse
from app.core.security import get_current_user
from app.core.config import settings
from app.services.data_processor import process_dataset, load_dataset
from app.services.notification_service import notify_dataset_upload, notify_dataset_error

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


@router.post("/upload", response_model=DatasetResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    name: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not supported.")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_filename = f"{current_user.id}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    dataset = Dataset(name=name, filename=file.filename, file_path=file_path, owner_id=current_user.id, status="uploaded")
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    try:
        result = process_dataset(file_path)
        dataset.rows_count = result["rows"]
        dataset.columns_info = result["columns"]
        dataset.status = "processed"
        db.commit()
        db.refresh(dataset)
        notify_dataset_upload(db, current_user.id, name, result["rows"])
    except Exception as e:
        dataset.status = "error"
        dataset.error_message = str(e)
        db.commit()
        db.refresh(dataset)
        notify_dataset_error(db, current_user.id, name, str(e))

    return dataset


@router.get("/")
def list_datasets(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Dataset).filter(Dataset.owner_id == current_user.id)
    if search:
        query = query.filter(Dataset.name.contains(search))
    if status:
        query = query.filter(Dataset.status == status)
    total = query.count()
    datasets = query.order_by(Dataset.created_at.desc()).offset(skip).limit(limit).all()
    return {"total": total, "datasets": datasets}


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/{dataset_id}/preview")
def preview_dataset(dataset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = load_dataset(dataset.file_path)
    return {
        "columns": df.columns.tolist(),
        "preview": df.head(10).to_dict(orient="records"),
        "shape": {"rows": len(df), "cols": len(df.columns)},
        "dtypes": df.dtypes.astype(str).to_dict(),
        "stats": df.describe().round(2).to_dict(),
    }


@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if os.path.exists(dataset.file_path):
        os.remove(dataset.file_path)
    db.delete(dataset)
    db.commit()
    return {"message": "Dataset deleted successfully"}
