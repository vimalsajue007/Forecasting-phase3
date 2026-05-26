"""
Anomaly Detection using IQR + Z-Score methods.
Detects unusual sales patterns in time series data.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List


def detect_anomalies(
    file_path: str,
    date_column: str,
    target_column: str,
    sensitivity: float = 1.5,
) -> Dict[str, Any]:
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
    df = df.dropna(subset=[date_column, target_column])
    df = df.sort_values(date_column)
    df[target_column] = pd.to_numeric(df[target_column], errors="coerce").fillna(0)

    values = df[target_column].values

    # IQR method
    Q1 = np.percentile(values, 25)
    Q3 = np.percentile(values, 75)
    IQR = Q3 - Q1
    lower_iqr = Q1 - sensitivity * IQR
    upper_iqr = Q3 + sensitivity * IQR

    # Z-score method
    mean = np.mean(values)
    std = np.std(values)
    z_threshold = 2.5

    anomalies = []
    for idx, row in df.iterrows():
        val = float(row[target_column])
        ds = str(row[date_column])[:10]
        z_score = abs((val - mean) / std) if std > 0 else 0
        is_iqr = val < lower_iqr or val > upper_iqr
        is_zscore = z_score > z_threshold

        if is_iqr or is_zscore:
            direction = "high" if val > upper_iqr or val > mean + z_threshold * std else "low"
            severity = "high" if (is_iqr and is_zscore) else "medium" if is_zscore else "low"
            anomalies.append({
                "date": ds,
                "value": round(val, 2),
                "expected_min": round(lower_iqr, 2),
                "expected_max": round(upper_iqr, 2),
                "z_score": round(z_score, 3),
                "direction": direction,
                "severity": severity,
            })

    # Seasonal analysis
    seasonal_insights = _analyze_seasonality(df, date_column, target_column)

    # Summary
    high_count = sum(1 for a in anomalies if a["severity"] == "high")
    overall_severity = "high" if high_count > 3 else "medium" if len(anomalies) > 2 else "low"

    summary = (
        f"Found {len(anomalies)} anomalies in {len(df)} data points. "
        f"{high_count} high-severity anomalies detected. "
        f"Data range: {round(values.min(), 2)} to {round(values.max(), 2)}. "
        f"Mean: {round(mean, 2)}, Std: {round(std, 2)}."
    )

    return {
        "anomalies": anomalies,
        "anomaly_count": len(anomalies),
        "severity": overall_severity,
        "summary": summary,
        "statistics": {
            "mean": round(mean, 2),
            "std": round(std, 2),
            "Q1": round(Q1, 2),
            "Q3": round(Q3, 2),
            "lower_bound": round(lower_iqr, 2),
            "upper_bound": round(upper_iqr, 2),
            "total_points": len(df),
        },
        "seasonal_insights": seasonal_insights,
    }


def _analyze_seasonality(df: pd.DataFrame, date_col: str, target_col: str) -> Dict:
    try:
        df["_month"] = pd.to_datetime(df[date_col]).dt.month
        df["_quarter"] = pd.to_datetime(df[date_col]).dt.quarter

        monthly = df.groupby("_month")[target_col].mean().round(2).to_dict()
        quarterly = df.groupby("_quarter")[target_col].mean().round(2).to_dict()

        peak_month = max(monthly, key=monthly.get) if monthly else None
        low_month = min(monthly, key=monthly.get) if monthly else None

        month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
                       7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

        return {
            "monthly_avg": {month_names.get(k, k): v for k, v in monthly.items()},
            "quarterly_avg": {f"Q{k}": v for k, v in quarterly.items()},
            "peak_month": month_names.get(peak_month, peak_month),
            "low_month": month_names.get(low_month, low_month),
        }
    except Exception:
        return {}
