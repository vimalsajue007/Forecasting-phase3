"""
Middleware for activity logging and performance tracking.
"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class ActivityLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response: Response = await call_next(request)
        duration_ms = int((time.time() - start_time) * 1000)

        # Only log API calls
        if request.url.path.startswith("/api/"):
            try:
                from app.db.database import SessionLocal
                from app.services.activity_service import log_activity
                from app.core.security import get_current_user
                from jose import jwt
                from app.core.config import settings

                user_id = None
                auth_header = request.headers.get("Authorization", "")
                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    try:
                        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                        username = payload.get("sub")
                        if username:
                            db = SessionLocal()
                            from app.models.user import User
                            user = db.query(User).filter(User.username == username).first()
                            if user:
                                user_id = user.id
                            db.close()
                    except Exception:
                        pass

                db = SessionLocal()
                action = f"{request.method}:{request.url.path.split('/')[2] if len(request.url.path.split('/')) > 2 else 'root'}"
                log_activity(
                    db,
                    action=action,
                    user_id=user_id,
                    method=request.method,
                    endpoint=str(request.url.path),
                    status_code=response.status_code,
                    ip_address=request.client.host if request.client else None,
                    response_time_ms=duration_ms,
                )
                db.close()
            except Exception:
                pass

        response.headers["X-Response-Time"] = str(duration_ms)
        return response
