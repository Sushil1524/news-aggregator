from bson import ObjectId
from app.utils.supabase_auth import supabase
from app.config.mongo import articles_collection, analytics_collection
import redis
import json, os, dotenv
from datetime import datetime, timedelta, date

# Redis connection
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

USER_VIEW_KEY_PREFIX = "user_views:"

class AnalyticsService:

    # -------------------------
    # Site-wide analytics
    # -------------------------
    def get_trending_articles(self, limit: int = 10):
        """
        Returns top articles by views and upvotes combined.
        """
        articles = list(
            articles_collection.find()
            .sort([("views", -1), ("upvotes", -1)])
            .limit(limit)
        )
        for a in articles:
            a["_id"] = str(a["_id"])
        return articles

    def get_top_categories(self, limit: int = 5):
        """
        Returns top categories based on number of articles.
        """
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        result = list(articles_collection.aggregate(pipeline))
        return [{"category": r["_id"], "count": r["count"]} for r in result]

    def get_daily_article_counts(self, days: int = 7):
        """
        Returns number of articles published per day for the last N days.
        """
        today = datetime.utcnow()
        start_date = today - timedelta(days=days)
        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        result = list(articles_collection.aggregate(pipeline))
        return result

    # -------------------------
    # User-specific analytics
    # -------------------------
    def track_article_read(self, user_id: str, article_id: str, reading_time_seconds: int | None = None):
        """
        Tracks that a user has read an article.
        - stores a per-user read in Redis for batching
        - updates the user's gamification column in Supabase with:
            - reading_history (no duplicates, stores article_id + timestamp + reading_time)
            - total_articles_read (unique)
            - last_read_date / last_read_at
            - streak (simple day-based logic)
        """
        if not user_id:
            return False

        now = datetime.utcnow()
        now_iso = now.isoformat()
        key = f"{USER_VIEW_KEY_PREFIX}{user_id}"

        # store read in Redis for batching/analytics (store as string id)
        try:
            # store reading timestamp (ISO) and optional reading_time as JSON string for this article id
            payload = json.dumps({"ts": now_iso, "reading_time": reading_time_seconds})
            r.hset(key, str(article_id), payload)
            r.expire(key, 3600 * 24)
        except Exception as e:
            print(f"[Analytics] Redis HSET failed for user {user_id}: {e}")

        # Update Supabase gamification immediately (merge reading_history + streak)
        try:
            resp = supabase.table("users").select("gamification").eq("id", user_id).single().execute()
            gam = {}
            if resp and resp.data:
                gam = resp.data.get("gamification") or {}
                if isinstance(gam, str):
                    try:
                        gam = json.loads(gam)
                    except Exception:
                        gam = {}
            if not isinstance(gam, dict):
                gam = {}

            # reading_history: list of dicts {"article_id": "<id>", "timestamp": "<iso>", "reading_time": <int|null>}
            reading_history = gam.get("reading_history", [])
            if not isinstance(reading_history, list):
                reading_history = []

            # Avoid duplicates: check by article_id string
            article_id_str = str(article_id)
            already_read = any(entry.get("article_id") == article_id_str for entry in reading_history)
            if not already_read:
                entry = {"article_id": article_id_str, "timestamp": now_iso}
                if reading_time_seconds is not None:
                    entry["reading_time_seconds"] = int(reading_time_seconds)
                else:
                    entry["reading_time_seconds"] = None
                reading_history.append(entry)

            # total articles read (unique)
            total_articles_read = len({entry.get("article_id") for entry in reading_history})

            # streak logic (day-based)
            last_read_date_str = gam.get("last_read_date")
            streak = gam.get("streak", 0) or 0
            try:
                last_read_date = datetime.fromisoformat(last_read_date_str).date() if last_read_date_str else None
            except Exception:
                last_read_date = None

            today = now.date()
            yesterday = today - timedelta(days=1)

            if last_read_date == today:
                # already read today — do not increment streak
                pass
            elif last_read_date == yesterday:
                streak = streak + 1
            else:
                # new streak start
                streak = 1

            # update gam fields
            gam["reading_history"] = reading_history
            gam["total_articles_read"] = total_articles_read
            gam["last_read_date"] = now_iso
            gam["last_read_at"] = now_iso
            gam["streak"] = streak

            # push update to Supabase
            supabase.table("users").update({"gamification": gam}).eq("id", user_id).execute()
        except Exception as e:
            print(f"[Analytics] Failed to update gamification for user {user_id}: {e}")

        return True

    def flush_user_reads(self):
        """
        Flush per-user article reads from Redis to MongoDB and update gamification in Supabase.
        """
        keys = r.keys(f"{USER_VIEW_KEY_PREFIX}*")
        for key in keys:
            user_id = key.replace(USER_VIEW_KEY_PREFIX, "")
            article_views = r.hgetall(key)
            if not article_views:
                continue

            # Convert article IDs to string ids and timestamps to datetime
            updates = []
            for a_id, payload in article_views.items():
                try:
                    data = json.loads(payload)
                    ts = data.get("ts")
                    reading_time = data.get("reading_time")
                except Exception:
                    ts = None
                    reading_time = None
                try:
                    ts_dt = datetime.fromisoformat(ts) if ts else datetime.utcnow()
                except Exception:
                    ts_dt = datetime.utcnow()
                updates.append({"article_id_str": str(a_id), "timestamp": ts_dt, "reading_time": reading_time})

            if not updates:
                r.delete(key)
                continue

            # Update MongoDB analytics (store string ids to keep responses JSON serializable)
            try:
                articles_ids = [u["article_id_str"] for u in updates if u.get("article_id_str")]
                reading_history_push = [{"article_id": u["article_id_str"], "timestamp": u["timestamp"], "reading_time_seconds": u.get("reading_time")} for u in updates]
                analytics_collection.update_one(
                    {"user_id": user_id},
                    {
                        "$addToSet": {"articles_read_ids": {"$each": articles_ids}},
                        "$push": {"reading_history": {"$each": reading_history_push}},
                        "$set": {"last_updated": datetime.utcnow()}
                    },
                    upsert=True
                )
            except Exception as e:
                print(f"[Analytics] Failed to update Mongo analytics for user {user_id}: {e}")

            # ----------------------
            # Update gamification in Supabase (merge reading_history without duplicates)
            # ----------------------
            try:
                resp = supabase.table("users").select("gamification").eq("id", user_id).single().execute()
                if resp.data:
                    current_gam = resp.data.get("gamification") or {}
                    if isinstance(current_gam, str):
                        try:
                            current_gam = json.loads(current_gam)
                        except Exception:
                            current_gam = {}
                else:
                    current_gam = {}

                if not isinstance(current_gam, dict):
                    current_gam = {}

                existing_history = current_gam.get("reading_history", [])
                if not isinstance(existing_history, list):
                    existing_history = []

                # Merge without duplicates, preserve timestamps (prefer existing)
                existing_ids = {str(entry.get("article_id")) for entry in existing_history if entry.get("article_id")}
                for u in updates:
                    a_id = u["article_id_str"]
                    if a_id not in existing_ids:
                        existing_history.append({"article_id": a_id, "timestamp": u["timestamp"].isoformat(), "reading_time_seconds": u.get("reading_time")})
                        existing_ids.add(a_id)

                current_gam["reading_history"] = existing_history
                current_gam["total_articles_read"] = len(existing_ids)

                # streak: simple update based on distinct new reads; you can refine with date logic
                current_gam["streak"] = current_gam.get("streak", 0) + len([u for u in updates if u["article_id_str"] not in existing_ids])
                current_gam["last_read_date"] = datetime.utcnow().isoformat()

                supabase.table("users").update({"gamification": current_gam}).eq("id", user_id).execute()
            except Exception as e:
                print(f"[Analytics] Failed to flush gamification for user {user_id}: {e}")

            # Clear Redis key
            r.delete(key)

    def get_user_dashboard_data(self, user_id: str):
        """
        Retrieves analytics data for a user's dashboard.
        Combines Supabase gamification data with reading history from MongoDB.
        """
        # Fetch user gamification and username from Supabase
        user_resp = supabase.table("users").select("username, gamification").eq("id", user_id).single().execute()
        if not user_resp.data:
            raise ValueError("User not found")

        user_data = user_resp.data

        # Ensure gamification is a dict, not a JSON string
        gamification = user_data.get("gamification", {})
        if isinstance(gamification, str):
            try:
                gamification = json.loads(gamification)
            except Exception:
                gamification = {}

        # Fetch analytics from MongoDB (user_id stored as string)
        analytics_doc = analytics_collection.find_one({"user_id": user_id}) or {}

        # Normalize reading_history and article ids to JSON-safe types
        raw_history = analytics_doc.get("reading_history", [])
        reading_history = []
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        recent_count = 0
        for entry in raw_history:
            art_id = entry.get("article_id")
            ts = entry.get("timestamp")
            # convert ObjectId or other types to string
            art_id_str = str(art_id) if art_id is not None else None
            # normalize timestamp to ISO
            ts_iso = None
            if isinstance(ts, datetime):
                ts_iso = ts.isoformat()
            else:
                try:
                    ts_dt = datetime.fromisoformat(str(ts))
                    ts_iso = ts_dt.isoformat()
                except Exception:
                    ts_iso = None
            reading_history.append({"article_id": art_id_str, "timestamp": ts_iso, "reading_time_seconds": entry.get("reading_time_seconds")})
            if ts_iso:
                try:
                    ts_dt = datetime.fromisoformat(ts_iso)
                    if ts_dt >= one_week_ago:
                        recent_count += 1
                except Exception:
                    pass

        articles_read_ids = analytics_doc.get("articles_read_ids", [])
        articles_read_ids = [str(a) for a in articles_read_ids]

        return {
            "username": user_data.get("username"),
            "points": gamification.get("points", 0),
            "streak": gamification.get("streak", 0),
            "articles_read_total": len(articles_read_ids),
            "articles_read_last_week": recent_count,
            "vocab_words_added": analytics_doc.get("vocab_added_count", 0),
            "reading_history": reading_history
        }

analytics_service = AnalyticsService()