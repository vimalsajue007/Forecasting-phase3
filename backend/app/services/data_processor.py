import pandas as pd
import numpy as np
from typing import Dict, Any


def load_dataset(file_path: str) -> pd.DataFrame:
    """Load CSV or Excel file into DataFrame."""
    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    return df


def process_dataset(file_path: str) -> Dict[str, Any]:
    """
    Process uploaded dataset:
    - Validate structure
    - Handle missing values
    - Remove duplicates
    - Return metadata
    """
    df = load_dataset(file_path)

    # Remove duplicates
    original_rows = len(df)
    df = df.drop_duplicates()

    # Handle missing values
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=["object"]).columns

    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    df[categorical_cols] = df[categorical_cols].fillna(df[categorical_cols].mode().iloc[0] if not df[categorical_cols].empty else "Unknown")

    # Save cleaned file back
    if file_path.endswith(".csv"):
        df.to_csv(file_path, index=False)
    else:
        df.to_excel(file_path, index=False)

    columns_info = []
    for col in df.columns:
        col_info = {
            "name": col,
            "dtype": str(df[col].dtype),
            "null_count": int(df[col].isnull().sum()),
            "unique_count": int(df[col].nunique()),
        }
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info["min"] = float(df[col].min())
            col_info["max"] = float(df[col].max())
            col_info["mean"] = float(df[col].mean())
        columns_info.append(col_info)

    return {
        "rows": len(df),
        "original_rows": original_rows,
        "duplicates_removed": original_rows - len(df),
        "columns": columns_info,
    }
