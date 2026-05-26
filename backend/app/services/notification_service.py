from sqlalchemy.orm import Session
from app.models.notification import Notification


def create_notification(db: Session, user_id: int, title: str, message: str, type: str = "info"):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def notify_forecast_complete(db: Session, user_id: int, forecast_name: str, accuracy: float = None):
    acc_text = f" with {round(accuracy * 100, 1)}% accuracy" if accuracy else ""
    create_notification(
        db, user_id,
        title="Forecast Completed ✅",
        message=f"Your forecast '{forecast_name}' has been completed{acc_text}.",
        type="success",
    )


def notify_forecast_error(db: Session, user_id: int, forecast_name: str, error: str):
    create_notification(
        db, user_id,
        title="Forecast Failed ❌",
        message=f"Forecast '{forecast_name}' failed: {error[:100]}",
        type="error",
    )


def notify_dataset_upload(db: Session, user_id: int, dataset_name: str, rows: int):
    create_notification(
        db, user_id,
        title="Dataset Uploaded ✅",
        message=f"Dataset '{dataset_name}' uploaded successfully with {rows:,} rows.",
        type="success",
    )


def notify_dataset_error(db: Session, user_id: int, dataset_name: str, error: str):
    create_notification(
        db, user_id,
        title="Dataset Upload Failed ❌",
        message=f"Dataset '{dataset_name}' failed to process: {error[:100]}",
        type="error",
    )


def notify_report_generated(db: Session, user_id: int, forecast_name: str, report_type: str):
    create_notification(
        db, user_id,
        title="Report Ready 📄",
        message=f"{report_type.upper()} report for '{forecast_name}' is ready to download.",
        type="info",
    )
