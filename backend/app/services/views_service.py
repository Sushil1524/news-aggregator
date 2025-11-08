import redis
from app.config.mongo import articles_collection
from app.services.analytics_service import analytics_service
from datetime import datetime
from bson import ObjectId

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

VIEW_KEY_PREFIX = "article_views:"       # global article views
USER_VIEW_KEY_PREFIX = "user_views:"     # per-user article reads for analytics

# -----------------------------
# Increment view counts
# -----------------------------
def increment_article_view(article_id: str, user_id: str | None = None):
    """
    Increment global article view count in Redis.
    """
    print("Incrementing view for article:", article_id, "by user:", user_id)
    article_key = f"{VIEW_KEY_PREFIX}{article_id}"
    r.incr(article_key)
    r.expire(article_key, 3600 * 24)

    # Delegate user read tracking to analytics_service
    if user_id:
        analytics_service.track_article_read(user_id, article_id)


# -----------------------------
# Flush Redis views to MongoDB
# -----------------------------
def flush_views_to_db():
    """
    Flush global article views to MongoDB.
    """
    print("Flushing article views from Redis to MongoDB...")
    keys = r.keys(f"{VIEW_KEY_PREFIX}*")
    for key in keys:
        article_id = key.replace(VIEW_KEY_PREFIX, "")
        count = int(r.get(key))
        if count > 0:
            try:
                articles_collection.update_one(
                    {"_id": ObjectId(article_id)},
                    {"$inc": {"views": count}}
                )
            except Exception as e:
                print(f"Failed to flush views for {article_id}: {e}")
            r.delete(key)
