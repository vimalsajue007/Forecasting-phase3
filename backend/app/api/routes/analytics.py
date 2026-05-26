"""
Advanced Analytics — region-wise, category-wise, revenue prediction, inventory risk.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
import pandas as pd
import numpy as np

from app.db.database import get_db
from app.models.user import User
from app.models.dataset import Dataset
from app.models.forecast import Forecast
from app.core.security import get_current_user
from app.core.roles import require_permission
from app.services.data_processor import load_dataset
from app.core.cache import get_cache, set_cache

router = APIRouter(prefix="/api/analytics", tags=["Advanced Analytics"])


@router.get("/region-wise")
def region_wise_analytics(
    dataset_id: int,
    date_column: str = "date",
    value_column: str = "sales",
    region_column: str = "region",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytics")),
):
    cache_key = f"analytics:region:{dataset_id}:{current_user.id}"
    cached = get_cache(db, cache_key)
    if cached:
        return cached

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset(dataset.file_path)
    if region_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{region_column}' not found")

    df[value_column] = pd.to_numeric(df[value_column], errors="coerce").fillna(0)

    region_stats = df.groupby(region_column)[value_column].agg(
        total="sum", mean="mean", count="count", std="std"
    ).round(2).reset_index()

    total = region_stats["total"].sum()
    region_stats["share_pct"] = (region_stats["total"] / total * 100).round(1)

    if date_column in df.columns:
        df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
        df["_month"] = df[date_column].dt.to_period("M").astype(str)
        trend = df.groupby([region_column, "_month"])[value_column].sum().reset_index()
        trend_data = {}
        for region in trend[region_column].unique():
            r_data = trend[trend[region_column] == region].sort_values("_month")
            trend_data[str(region)] = r_data[["_month", value_column]].rename(
                columns={"_month": "month", value_column: "sales"}
            ).to_dict(orient="records")
    else:
        trend_data = {}

    result = {
        "regions": region_stats.to_dict(orient="records"),
        "trends": trend_data,
        "top_region": region_stats.loc[region_stats["total"].idxmax(), region_column] if len(region_stats) > 0 else None,
        "total_value": round(float(total), 2),
    }
    set_cache(db, cache_key, result, ttl_seconds=300)
    return result


@router.get("/category-wise")
def category_wise_analytics(
    dataset_id: int,
    value_column: str = "sales",
    category_column: str = "product",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytics")),
):
    cache_key = f"analytics:category:{dataset_id}:{current_user.id}"
    cached = get_cache(db, cache_key)
    if cached:
        return cached

    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset(dataset.file_path)
    if category_column not in df.columns:
        raise HTTPException(status_code=400, detail=f"Column '{category_column}' not found")

    df[value_column] = pd.to_numeric(df[value_column], errors="coerce").fillna(0)

    cat_stats = df.groupby(category_column)[value_column].agg(
        total="sum", mean="mean", count="count"
    ).round(2).reset_index().sort_values("total", ascending=False)

    total = cat_stats["total"].sum()
    cat_stats["share_pct"] = (cat_stats["total"] / total * 100).round(1)

    result = {
        "categories": cat_stats.head(20).to_dict(orient="records"),
        "top_category": cat_stats.iloc[0][category_column] if len(cat_stats) > 0 else None,
        "total_categories": len(cat_stats),
        "total_value": round(float(total), 2),
    }
    set_cache(db, cache_key, result, ttl_seconds=300)
    return result


@router.get("/revenue-prediction")
def revenue_prediction(
    dataset_id: int,
    date_column: str = "date",
    value_column: str = "sales",
    forecast_months: int = Query(3, ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytics")),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset(dataset.file_path)
    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df[value_column] = pd.to_numeric(df[value_column], errors="coerce").fillna(0)
    df = df.dropna(subset=[date_column]).sort_values(date_column)

    monthly = df.groupby(df[date_column].dt.to_period("M"))[value_column].sum()
    monthly.index = monthly.index.astype(str)

    if len(monthly) < 2:
        raise HTTPException(status_code=400, detail="Not enough monthly data for prediction")

    values = monthly.values
    growth_rate = float(np.mean(np.diff(values) / (values[:-1] + 1e-8)))
    last_value = float(values[-1])

    predictions = []
    for i in range(1, forecast_months + 1):
        predicted = last_value * (1 + growth_rate) ** i
        predictions.append({
            "month": f"Month+{i}",
            "predicted_revenue": round(max(0, predicted), 2),
            "growth_rate_pct": round(growth_rate * 100, 2),
        })

    return {
        "historical_monthly": [{"month": k, "revenue": round(float(v), 2)} for k, v in monthly.items()],
        "predictions": predictions,
        "avg_monthly_revenue": round(float(np.mean(values)), 2),
        "growth_trend": "positive" if growth_rate > 0 else "negative",
        "avg_growth_rate_pct": round(growth_rate * 100, 2),
    }


@router.get("/inventory-risk")
def inventory_risk_analysis(
    dataset_id: int,
    value_column: str = "sales",
    date_column: str = "date",
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("view_analytics")),
):
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id, Dataset.owner_id == current_user.id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = load_dataset(dataset.file_path)
    df[value_column] = pd.to_numeric(df[value_column], errors="coerce").fillna(0)

    values = df[value_column].values
    mean_demand = float(np.mean(values))
    std_demand = float(np.std(values))
    cv = std_demand / mean_demand if mean_demand > 0 else 0

    # Risk classification
    if cv > 0.5:
        risk_level = "high"
        risk_message = "High demand variability — consider safety stock buffers"
    elif cv > 0.25:
        risk_level = "medium"
        risk_message = "Moderate demand variability — review replenishment cycles"
    else:
        risk_level = "low"
        risk_message = "Stable demand — standard inventory management sufficient"

    # Safety stock recommendation (1.65 sigma for 95% service level)
    safety_stock = 1.65 * std_demand
    reorder_point = mean_demand + safety_stock

    # Demand spikes
    upper_threshold = mean_demand + 2 * std_demand
    lower_threshold = max(0, mean_demand - 2 * std_demand)
    spikes = int(np.sum(values > upper_threshold))
    stockouts = int(np.sum(values < lower_threshold))

    return {
        "risk_level": risk_level,
        "risk_message": risk_message,
        "coefficient_of_variation": round(cv, 4),
        "mean_demand": round(mean_demand, 2),
        "std_demand": round(std_demand, 2),
        "recommended_safety_stock": round(safety_stock, 2),
        "recommended_reorder_point": round(reorder_point, 2),
        "demand_spikes": spikes,
        "potential_stockouts": stockouts,
        "insights": [
            f"Average demand: {round(mean_demand, 2)} units",
            f"Demand variability (CV): {round(cv * 100, 1)}%",
            f"Recommended safety stock: {round(safety_stock, 2)} units",
            f"Detected {spikes} demand spikes in dataset",
        ],
    }


@router.get("/global-search")
def global_search(
    q: str = Query(..., min_length=2),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    results = {"datasets": [], "forecasts": [], "total": 0}

    datasets = db.query(Dataset).filter(
        Dataset.owner_id == current_user.id,
        Dataset.name.contains(q),
    ).limit(5).all()
    results["datasets"] = [{"id": d.id, "name": d.name, "type": "dataset", "status": d.status} for d in datasets]

    forecasts = db.query(Forecast).filter(
        Forecast.owner_id == current_user.id,
        Forecast.name.contains(q),
    ).limit(5).all()
    results["forecasts"] = [{"id": f.id, "name": f.name, "type": "forecast", "status": f.status, "model": f.model_type} for f in forecasts]

    results["total"] = len(results["datasets"]) + len(results["forecasts"])
    return results
