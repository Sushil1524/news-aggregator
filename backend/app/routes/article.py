from fastapi import APIRouter, HTTPException, Depends, Query, Request, Header
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta
from app.models.article_model import ArticleDB
from app.config.mongo import articles_collection
from app.utils.dependencies import get_current_user
from fastapi import Request
from fastapi.security.utils import get_authorization_scheme_param
from app.services.views_service import increment_article_view
from app.utils.supabase_auth import verify_token

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
    tag: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("new"),  # default: newest first
    date_filter: Optional[str] = Query(None)  # e.g. 'today', 'last_hour'
):
    query = {}

    # Category / tag filters
    if category:
        query["category"] = category
    if tag:
        query["tags"] = tag

    # Date filters
    now = datetime.utcnow()
    if date_filter == "today":
        query["created_at"] = {"$gte": datetime(now.year, now.month, now.day)}
    elif date_filter == "last_hour":
        query["created_at"] = {"$gte": now - timedelta(hours=1)}

    # Cursor-based pagination
    if cursor:
        query["created_at"] = {**query.get("created_at", {}), "$lt": cursor}

    # Sorting logic
    sort_field = "created_at"
    sort_order = -1  # descending by default

    if sort_by == "new":
        sort_field = "created_at"
        sort_order = -1
    elif sort_by == "old":
        sort_field = "created_at"
        sort_order = 1
    elif sort_by == "top":
        sort_field = "upvotes"
        sort_order = -1

    # Query MongoDB
    articles = list(
        articles_collection.find(query)
        .sort(sort_field, sort_order)
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
async def get_article(article_id: str, request: Request, x_reading_duration: Optional[int] = Header(None, alias="X-Reading-Duration")):
    article = articles_collection.find_one({"_id": ObjectId(article_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    # Try to extract user id from Bearer JWT (optional)
    user_id = None
    try:
        auth = request.headers.get("Authorization")
        if auth:
            scheme, token = get_authorization_scheme_param(auth)
            if scheme and scheme.lower() == "bearer" and token:
                payload = verify_token(token)
                if payload and isinstance(payload, dict):
                    user_id = payload.get("id") or payload.get("sub")
    except Exception:
        user_id = None

    # increment views (will track per-user read if user_id present)
    # pass optional reading duration (seconds) if provided via header
    increment_article_view(article_id, user_id, reading_time_seconds=x_reading_duration)

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