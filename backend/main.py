import os
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import create_tables
from app.api.routes import auth, datasets, forecasts, dashboard, reports, notifications, admin
from app.api.routes import analytics, monitoring, anomaly
from app.core.config import settings
from app.core.middleware import ActivityLogMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    create_tables()
    yield


app = FastAPI(
    title="AI Demand Forecasting API",
    description="Enterprise-grade AI-powered demand forecasting platform",
    version="3.0.0",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title="AI Demand Forecasting API",
        version="3.0.0",
        routes=app.routes,
    )
    schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = schema
    return schema

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Activity logging middleware
app.add_middleware(ActivityLogMiddleware)
app.openapi = custom_openapi
# Routers
app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(forecasts.router)
app.include_router(dashboard.router)
app.include_router(reports.router)
app.include_router(notifications.router)
app.include_router(admin.router)
app.include_router(analytics.router)
app.include_router(monitoring.router)
app.include_router(anomaly.router)

app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {"message": "AI Demand Forecasting API v3.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy", "version": "3.0.0"}
