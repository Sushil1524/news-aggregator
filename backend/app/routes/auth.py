# app/routes/auth.py
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.user_model import UserCreate, UserLogin, TokenResponse, UserRole
from app.utils.supabase_auth import (
    supabase,
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.utils.dependencies import get_current_user
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
        "role": UserRole.USER.value,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }).execute()

    if not result.data:
        raise HTTPException(status_code=500, detail="Registration failed")

    # Create JWT tokens
    token_data = {"sub": user.username, "role": UserRole.USER.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    # Determine login method (email or username)
    if user.email:
        query = supabase.table("users").select("*").eq("email", user.email)
    elif user.username:
        query = supabase.table("users").select("*").eq("username", user.username)
    else:
        raise HTTPException(status_code=400, detail="Email or username required")

    result = query.execute()
    if not result.data:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    db_user = result.data[0]

    # Verify password
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Prepare token payload
    user_role = db_user.get("role", UserRole.USER.value)
    token_data = {"sub": db_user["username"], "role": user_role, "id": db_user["id"]}

    # Generate JWT tokens
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.get("/me")
def get_current_user_data(current_user: dict = Depends(get_current_user)):
    """
    Fetch the current logged-in user's basic data from Supabase.
    """
    user_id = current_user.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token or user ID.")

    response = supabase.table("users").select("*").eq("id", user_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")

    # Return only basic data (filtering sensitive fields if needed)
    user = response.data[0]
    user.pop("password", None)
    user.pop("refresh_token", None)
    return {"user": user}