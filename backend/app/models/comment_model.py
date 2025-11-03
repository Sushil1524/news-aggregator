from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CommentBase(BaseModel):
    article_id: str                  # Article to which this comment belongs
    content: str
    parent_id: Optional[str] = None  # For replies

class CommentCreate(CommentBase):
    pass

class CommentDB(CommentBase):
    id: str = Field(..., alias="_id")
    author_email: str
    upvotes: int = 0
    downvotes: int = 0
    created_at: datetime
    updated_at: datetime
