# app/models/user_model.py
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date
from typing import Optional, List, Dict

class Gamification(BaseModel):
    points: int = 0
    streak: int = 0

class VocabCard(BaseModel):
    word: str
    meaning: Optional[str] = None
    example: Optional[str] = None
    added_at: datetime = Field(default_factory=datetime.utcnow)
    level: int = 1  # for spaced repetition / learning progress

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class VocabProficiency(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: str  # unique username for each user
    full_name: Optional[str] = None
    dob: Optional[date] = None  # Date of Birth
    vocab_proficiency: Optional[VocabProficiency] = VocabProficiency.BEGINNER
    daily_practice_target: Optional[int] = Field(
        10, description="Number of words user wants to practice daily"
    )
    news_preferences: Dict[str, bool] = Field(
        default_factory=lambda: {
            "Technology": True,
            "Politics": True,
            "Business": True,
            "Health": True,
            "Sports": True
        },
        description="User's preferences for news categories"
    )
    role: UserRole = Field(default=UserRole.USER, exclude=True)
    gamification: Gamification = Gamification()
    vocab_cards: List[VocabCard] = []  # for card-based vocab learning
    bookmarks: List[str] = []  # list of bookmarked article IDs

class TokenResponse(BaseModel): 
    access_token: str 
    refresh_token: str 
    token_type: str = "bearer"

class UserLogin(BaseModel): 
    email: EmailStr 
    username: str
    password: str
