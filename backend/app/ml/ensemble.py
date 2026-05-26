"""
Ensemble forecasting — combines multiple models for better accuracy.
Uses weighted average based on individual model R² scores.
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from app.ml.forecasting import _run_sklearn_model, _detect_frequency


def run_ensemble_forecast(
    file_path: str,
    periods: int,
    target_column: str,
    date_column: str,
    feature_columns: List[str],
    models: List[str] = None,
) -> Dict[str, Any]:
    if models is None:
        models = ["linear_regression", "ridge_regression", "random_forest", "gradient_boosting"]

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df = df.dropna(subset=[date_column, target_column])
    df = df.sort_values(date_column)

    results = []
    weights = []

    for model in models:
        try:
            result = _run_sklearn_model(df, date_column, target_column, feature_columns, periods, model)
            r2 = result.get("r2_score", 0)
            results.append(result)
            weights.append(max(r2, 0.01))  # min weight 0.01
        except Exception:
            pass

    if not results:
        raise ValueError("All models failed to train")

    # Normalize weights
    total_weight = sum(weights)
    norm_weights = [w / total_weight for w in weights]

    # Weighted ensemble predictions
    num_preds = len(results[0]["predictions"])
    ensemble_preds = []
    for i in range(num_preds):
        weighted_yhat = sum(
            results[j]["predictions"][i]["yhat"] * norm_weights[j]
            for j in range(len(results))
            if i < len(results[j]["predictions"])
        )
        ensemble_preds.append({
            "ds": results[0]["predictions"][i]["ds"],
            "yhat": round(weighted_yhat, 2),
        })

    # Weighted metrics
    ensemble_r2 = sum(results[j].get("r2_score", 0) * norm_weights[j] for j in range(len(results)))
    ensemble_mae = sum(results[j].get("mae", 0) * norm_weights[j] for j in range(len(results)))
    ensemble_rmse = sum(results[j].get("rmse", 0) * norm_weights[j] for j in range(len(results)))

    model_contributions = [
        {
            "model": models[j],
            "weight": round(norm_weights[j] * 100, 1),
            "r2_score": round(results[j].get("r2_score", 0), 4),
        }
        for j in range(len(results))
    ]

    return {
        "predictions": ensemble_preds,
        "historical": results[0]["historical"],
        "r2_score": round(ensemble_r2, 4),
        "mae": round(ensemble_mae, 4),
        "rmse": round(ensemble_rmse, 4),
        "model_contributions": model_contributions,
        "models_used": len(results),
    }
