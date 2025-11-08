# app/routes/bookmarks.py

from fastapi import APIRouter, Depends, HTTPException
from app.utils.dependencies import get_current_user
from app.utils.supabase_auth import supabase
from app.config.mongo import articles_collection
from bson import ObjectId

USERS_TABLE = "users"
router = APIRouter()

# ---------------- Helper ----------------
def get_user_id_from_sub(sub: str):
    """
    Fetch the user's UUID from Supabase using the JWT 'sub' claim (username/email).
    """
    res = supabase.table(USERS_TABLE).select("id").eq("username", sub).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
    return res.data["id"]

# ---------------- Routes ----------------

@router.post("/{article_id}")
def add_user_bookmark(article_id: str, user=Depends(get_current_user)):
    """
    Add an article ID to the current user's bookmarks array in Supabase.
    """
    user_sub = user.get("sub")
    user_id = get_user_id_from_sub(user_sub)

    user_data = supabase.table(USERS_TABLE).select("bookmarks").eq("id", user_id).single().execute()
    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")

    bookmarks = user_data.data.get("bookmarks") or []
    if article_id in bookmarks:
        raise HTTPException(status_code=400, detail="Bookmark already exists")

    bookmarks.append(article_id)
    supabase.table(USERS_TABLE).update({"bookmarks": bookmarks}).eq("id", user_id).execute()

    return {"message": "Bookmark added", "bookmarks": bookmarks}


@router.delete("/{article_id}")
def remove_user_bookmark(article_id: str, user=Depends(get_current_user)):
    """
    Remove an article ID from the current user's bookmarks array in Supabase.
    """
    user_sub = user.get("sub")
    user_id = get_user_id_from_sub(user_sub)

    user_data = supabase.table(USERS_TABLE).select("bookmarks").eq("id", user_id).single().execute()
    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")

    bookmarks = user_data.data.get("bookmarks") or []
    if article_id not in bookmarks:
        raise HTTPException(status_code=404, detail="Bookmark not found")

    bookmarks.remove(article_id)
    supabase.table(USERS_TABLE).update({"bookmarks": bookmarks}).eq("id", user_id).execute()

    return {"message": "Bookmark removed", "bookmarks": bookmarks}


@router.get("/")
def get_user_bookmarks_route(user=Depends(get_current_user)):
    """
    Retrieve full articles for the current user's bookmarks.
    """
    user_sub = user.get("sub")
    user_id = get_user_id_from_sub(user_sub)

    user_data = supabase.table(USERS_TABLE).select("bookmarks").eq("id", user_id).single().execute()
    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")

    article_ids = user_data.data.get("bookmarks") or []
    if not article_ids:
        return []

    try:
        object_ids = [ObjectId(aid) for aid in article_ids]
    except Exception:
        object_ids = []

    articles = list(articles_collection.find({"_id": {"$in": object_ids}}))

    # ✅ Serialize MongoDB ObjectIds to strings
    for article in articles:
        article["_id"] = str(article["_id"])

    return articles