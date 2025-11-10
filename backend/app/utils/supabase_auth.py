# app/utils/supabase_auth.py

import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi import HTTPException, Request

load_dotenv()

# Supabase client setup
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
USERS_TABLE = "users"

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

# ---------------------------
# Added method for FastAPI
# ---------------------------
async def get_current_user_data(request: Request):
    """
    FastAPI dependency to extract JWT from Authorization header,
    validate it, and return a cleaned user object.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user_email = payload.get("sub")
    role = payload.get("role", "user")  # default role if not in token
    if not user_email:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Fetch user from Supabase
    response = supabase.table("users").select("*").eq("username", user_email).execute()
    if not response.data or len(response.data) == 0:
        raise HTTPException(status_code=401, detail="User not found")

    db_user = response.data[0]

    # Return only relevant fields
    user_data = {
        "email": db_user["email"],
        "username": db_user.get("username"),
        "full_name": db_user.get("full_name"),
        "dob": db_user.get("dob"),
        "role": db_user.get("role", "user"),
        "gamification": db_user.get("gamification"),
        "vocab_proficiency": db_user.get("vocab_proficiency"),
        "daily_practice_target": db_user.get("daily_practice_target"),
        "vocab_cards": db_user.get("vocab_cards", []),
        "news_preferences": db_user.get("news_preferences", {}),
        "bookmarks": db_user.get("bookmarks", [])
    }

    return user_data

