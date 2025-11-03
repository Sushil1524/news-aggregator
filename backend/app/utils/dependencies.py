from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.supabase_auth import verify_token
from app.utils.supabase_auth import get_current_user_data

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return payload  # You can return email or full user info if stored in JWT

async def get_current_admin(user=Depends(get_current_user_data)):
    if not user.get("role") == "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user