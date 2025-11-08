from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
from app.models.article_model import ArticleDB
from app.config.mongo import articles_collection
from app.utils.dependencies import get_current_user
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from app.services.views_service import increment_article_view
from app.services.analytics_service import analytics_service

router = APIRouter()

# Helper: convert Mongo _id to string
def serialize_article(article) -> dict:
    article["_id"] = str(article["_id"])
    return article

# ---------------------
# List Articles (with optional category/tag filter & cursor-based pagination)
# ---------------------
@router.get("/", response_model=dict)
def get_articles(
    cursor: Optional[datetime] = Query(None),
    limit: int = 20,
    category: Optional[str] = Query(None),
    tag: Optional[str] = Query(None)
):
    query = {}
    if category:
        query["category"] = category
    if tag:
        query["tags"] = tag

    if cursor:
        query["created_at"] = {"$lt": cursor}

    # Fetch sorted by newest first
    articles = list(
        articles_collection.find(query)
        .sort("created_at", -1)
        .limit(limit)
    )

    next_cursor = articles[-1]["created_at"] if articles else None

    return {
        "articles": [serialize_article(a) for a in articles],
        "next_cursor": next_cursor
    }

# ---------------------
# Get Single Article
# ---------------------
@router.get("/{article_id}", response_model=ArticleDB)
def get_article(article_id: str, request: Request):
    # --- fetch article ---
    article = articles_collection.find_one({"_id": ObjectId(article_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # --- try optional user ---
    user = None
    try:
        # manually parse token if present
        auth = request.headers.get("Authorization")
        if auth:
            scheme, token = get_authorization_scheme_param(auth)
            if scheme.lower() == "bearer":
                from app.utils.dependencies import get_current_user
                user = get_current_user(token)
    except Exception as e:
        user = None  # ignore auth errors for public access

    # increment global views
    increment_article_view(article_id)

    return serialize_article(article)

# ---------------------
# Upvote Article
# ---------------------
@router.post("/{article_id}/upvote")
def upvote_article(article_id: str, user=Depends(get_current_user)):
    result = articles_collection.update_one(
        {"_id": ObjectId(article_id)},
        {"$inc": {"upvotes": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"detail": "Upvoted successfully"}

# ---------------------
# Downvote Article
# ---------------------
@router.post("/{article_id}/downvote")
def downvote_article(article_id: str, user=Depends(get_current_user)):
    result = articles_collection.update_one(
        {"_id": ObjectId(article_id)},
        {"$inc": {"downvotes": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"detail": "Downvoted successfully"}