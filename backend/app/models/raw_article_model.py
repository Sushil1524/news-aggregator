# app/models/raw_article_model.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class RawArticleBase(BaseModel):
    title: str
    url: str
    summary: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    tags: List[str] = []

class RawArticleDB(RawArticleBase):
    id: str = None
    created_at: datetime = None
