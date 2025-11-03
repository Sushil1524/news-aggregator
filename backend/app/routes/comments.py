from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
from app.models.comment_model import CommentCreate, CommentDB
from app.config.mongo import comments_collection, articles_collection
from app.utils.dependencies import get_current_user

router = APIRouter()

# Helper: serialize MongoDB _id
def serialize_comment(comment) -> dict:
    comment["_id"] = str(comment["_id"])
    return comment

# ---------------------
# Create Comment
# ---------------------
@router.post("/", response_model=CommentDB)
def create_comment(comment: CommentCreate, user=Depends(get_current_user)):
    """
    Create a comment or reply
    """
    # Check if article exists
    article = articles_collection.find_one({"_id": ObjectId(comment.article_id)})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    doc = comment.dict()
    doc["author_email"] = user["sub"]
    doc["upvotes"] = 0
    doc["downvotes"] = 0
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()

    result = comments_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    # Increment article's comments_count
    articles_collection.update_one(
        {"_id": ObjectId(comment.article_id)},
        {"$inc": {"comments_count": 1}}
    )

    return doc

# ---------------------
# Get Comments for an Article
# ---------------------
@router.get("/{article_id}", response_model=List[CommentDB])
def get_comments(article_id: str):
    comments = list(comments_collection.find({"article_id": article_id}).sort("created_at", 1))
    return [serialize_comment(c) for c in comments]

# ---------------------
# Delete Comment
# ---------------------
@router.delete("/{comment_id}")
def delete_comment(comment_id: str, user=Depends(get_current_user)):
    comment = comments_collection.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment["author_email"] != user["sub"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    comments_collection.delete_one({"_id": ObjectId(comment_id)})

    # Decrement comments_count in parent article
    articles_collection.update_one(
        {"_id": ObjectId(comment["article_id"])},
        {"$inc": {"comments_count": -1}}
    )

    return {"detail": "Comment deleted successfully"}

# ---------------------
# Upvote Comment
# ---------------------
@router.post("/{comment_id}/upvote")
def upvote_comment(comment_id: str, user=Depends(get_current_user)):
    result = comments_collection.update_one(
        {"_id": ObjectId(comment_id)},
        {"$inc": {"upvotes": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"detail": "Upvoted successfully"}

# ---------------------
# Downvote Comment
# ---------------------
@router.post("/{comment_id}/downvote")
def downvote_comment(comment_id: str, user=Depends(get_current_user)):
    result = comments_collection.update_one(
        {"_id": ObjectId(comment_id)},
        {"$inc": {"downvotes": 1}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Comment not found")
    return {"detail": "Downvoted successfully"}
