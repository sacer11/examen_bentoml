#jwt_auth.py 
import jwt as pyjwt
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

JWT_SECRET = "supersecret"
JWT_ALGORITHM = "HS256"

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path != "/login":
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            try:
                pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except Exception:
                raise HTTPException(status_code=401, detail="Invalid token")
        return await call_next(request)