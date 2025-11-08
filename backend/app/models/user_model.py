# app/models/user_model.py
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    gamification: Gamification = Gamification()
    vocab_cards: List[VocabCard] = []  # for card-based vocab learning
    bookmarks: List[str] = []  # list of bookmarked article IDs

class TokenResponse(BaseModel): 
    access_token: str 
    refresh_token: str 
    token_type: str = "bearer"

class UserLogin(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: str

    @field_validator("email", "username", mode="before")
    def empty_to_none(cls, v):
        if v == "":
            return None
        return v
    
    @model_validator(mode="after")
    def validate_login_method(self):
        if not self.email and not self.username:
            raise ValueError("Either 'email' or 'username' must be provided.")
        return self