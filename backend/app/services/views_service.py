import os
from dotenv import load_dotenv

# Ensure environment variables from a .env file are loaded at import time
load_dotenv()
from app.utils.redis_client import get_redis_client
from app.config.mongo import articles_collection
from app.services.analytics_service import analytics_service
from datetime import datetime
from bson import ObjectId

# Redis client (may be Upstash REST-based)
r = get_redis_client()

VIEW_KEY_PREFIX = "article_views:"       # global article views

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
    keys = r.keys(f"{VIEW_KEY_PREFIX}*") or []
    # Ensure we only process keys that actually start with the article prefix
    for key in list(keys):
        try:
            # Some clients may return bytes; normalize to str
            if isinstance(key, bytes):
                key = key.decode('utf-8')
            if not key.startswith(VIEW_KEY_PREFIX):
                continue

            article_id = key[len(VIEW_KEY_PREFIX):]

            # Safely get count (may return None or string)
            raw = r.get(key)
            try:
                count = int(raw) if raw is not None else 0
            except Exception:
                count = 0

            if count <= 0:
                # nothing to flush; remove stale key to avoid future noise
                try:
                    r.delete(key)
                except Exception:
                    pass
                continue

            # Persist to MongoDB; only delete Redis key if DB update succeeds
            try:
                articles_collection.update_one(
                    {"_id": ObjectId(article_id)},
                    {"$inc": {"views": count}}
                )
            except Exception as e:
                print(f"Failed to flush views for {article_id}: {e}")
                # don't delete the Redis key so the scheduler can retry later
                continue

            # Delete the Redis key only after successful DB update
            try:
                r.delete(key)
            except Exception as e:
                print(f"Failed to delete Redis key {key} after flushing: {e}")
                # Not critical; DB already updated
        except Exception as e:
            print(f"Unexpected error while flushing key {key}: {e}")
