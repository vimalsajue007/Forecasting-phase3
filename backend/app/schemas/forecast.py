from pydantic import BaseModel
from typing import Optional, List, Any, Dict
from datetime import datetime


class DatasetResponse(BaseModel):
    id: int
    name: str
    filename: str
    rows_count: int
    columns_info: Optional[Any] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ForecastCreate(BaseModel):
    name: str
    dataset_id: int
    model_type: str  # linear_regression or prophet
    periods: int
    target_column: str
    date_column: str
    feature_columns: Optional[List[str]] = None


class ForecastResponse(BaseModel):
    id: int
    name: str
    model_type: str
    periods: int
    accuracy_score: Optional[float] = None
    mae: Optional[float] = None
    rmse: Optional[float] = None
    predictions: Optional[Any] = None
    historical_data: Optional[Any] = None
    status: str
    error_message: Optional[str] = None
    dataset_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    total_datasets: int
    total_forecasts: int
    total_sales: float
    avg_accuracy: float
    monthly_trends: List[Dict[str, Any]]
    top_products: List[Dict[str, Any]]
    recent_forecasts: List[Dict[str, Any]]
