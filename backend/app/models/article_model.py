from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ArticleBase(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    category: Optional[str] = None          # e.g., "Tech", "Politics"
    tags: List[str] = []                    # Keywords
    sentiment: Optional[str] = None         # "positive", "negative", "neutral"

class ArticleCreate(ArticleBase):
    content: str

class ArticleDB(ArticleBase):
    id: str = Field(..., alias="_id")
    content: str
    author_email: str                        # Linked to user
    upvotes: int = 0
    downvotes: int = 0
    comments_count: int = 0
    views: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        validate_by_name = True
