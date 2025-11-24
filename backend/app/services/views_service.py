import os
import redis
from app.config.mongo import articles_collection
from app.services.analytics_service import analytics_service
from datetime import datetime
from bson import ObjectId

# Redis connection: prefer Upstash TLS URL (set UPSTASH_REDIS_URL or REDIS_URL),
# fallback to local Redis.
REDIS_URL = os.getenv("UPSTASH_REDIS_URL") or os.getenv("REDIS_URL")
try:
    if REDIS_URL:
        # redis.from_url handles rediss:// and redis:// schemes
        r = redis.from_url(REDIS_URL, decode_responses=True)
    else:
        r = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True,
        )
except Exception as e:
    print(f"Redis connection failed ({e}), falling back to localhost")
    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

VIEW_KEY_PREFIX = "article_views:"       # global article views
USER_VIEW_KEY_PREFIX = "user_views:"     # per-user article reads for analytics

# -----------------------------
# Increment view counts
# -----------------------------
def increment_article_view(article_id: str, user_id: str | None = None, reading_time_seconds: int | None = None):
    """
    Increment global article view count in Redis.
    If user_id provided, delegate to analytics_service.track_article_read
    and pass optional reading_time_seconds.
    """
    print("Incrementing view for article:", article_id, "by user:", user_id, "reading_time:", reading_time_seconds)
    article_key = f"{VIEW_KEY_PREFIX}{article_id}"
    try:
        r.incr(article_key)
        r.expire(article_key, 3600 * 24)
    except Exception as e:
        print(f"[Views] Redis INCR failed for {article_id}: {e}")

    # Delegate user read tracking to analytics_service
    if user_id:
        try:
            analytics_service.track_article_read(user_id, article_id, reading_time_seconds=reading_time_seconds)
        except Exception as e:
            print(f"[Views] analytics_service.track_article_read failed: {e}")


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
