# app/routes/auth.py
from fastapi import APIRouter, HTTPException
from app.models.user_model import UserCreate, UserLogin, TokenResponse, UserRole
from app.utils.supabase_auth import (
    supabase,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
import json

router = APIRouter()

@router.post("/register", response_model=TokenResponse)
def register(user: UserCreate):
    # Check if email or username already exists
    existing_email = supabase.table("users").select("*").eq("email", user.email).execute()
    if existing_email.data:
        raise HTTPException(status_code=400, detail="Email already exists")

    existing_username = supabase.table("users").select("*").eq("username", user.username).execute()
    if existing_username.data:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash password
    hashed_pw = hash_password(user.password)

    # Insert user with all fields
    result = supabase.table("users").insert({
        "email": user.email,
        "password": hashed_pw,
        "username": user.username,
        "full_name": user.full_name,
        "dob": user.dob.isoformat() if user.dob else None,
        "vocab_proficiency": user.vocab_proficiency.value if user.vocab_proficiency else "beginner",
        "daily_practice_target": user.daily_practice_target,
        "news_preferences": json.dumps(user.news_preferences),
        "gamification": json.dumps(user.gamification.dict()),
        "vocab_cards": json.dumps([card.dict() for card in user.vocab_cards]),
        "bookmarks": user.bookmarks,
        "role": UserRole.USER.value
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Registration failed")

    # Create JWT tokens
    token_data = {"sub": user.email, "role": UserRole.USER.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    # Determine whether login is email or username
    if "@" in user.email:
        query = supabase.table("users").select("*").eq("email", user.email)
    else:
        query = supabase.table("users").select("*").eq("username", user.email)

    result = query.execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Invalid email/username or password")

    db_user = result.data[0]

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email/username or password")

    user_role = db_user.get("role", UserRole.USER.value)
    token_data = {"sub": db_user["email"], "role": user_role}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

