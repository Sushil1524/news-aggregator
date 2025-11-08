from datetime import datetime, timedelta
from bson import ObjectId
from app.utils.supabase_auth import supabase
from app.config.mongo import articles_collection, analytics_collection
import redis
import json

# Redis connection
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
    def track_article_read(self, user_id: str, article_id: str):
        """
        Tracks that a user has read an article.
        Uses Redis for batching per-user reads.
        Updates gamification points/streak in Supabase.
        """
        now_iso = datetime.utcnow().isoformat()
        key = f"{USER_VIEW_KEY_PREFIX}{user_id}"
        r.hset(key, article_id, now_iso)
        r.expire(key, 3600 * 24)  # optional expiry (24 hours)

        # -----------------------------
        # Update points and streak in Supabase
        # -----------------------------
        user_resp = supabase.table("users").select("gamification").eq("id", user_id).single().execute()
        if user_resp.data:
            gamification = user_resp.data.get("gamification") or {"points": 0, "streak": 0}
            gamification["points"] = gamification.get("points", 0) + 1
            gamification["streak"] = gamification.get("streak", 0) + 1  # you can add logic for daily streak reset
            supabase.table("users").update({"gamification": gamification}).eq("id", user_id).execute()

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

            # Convert article IDs to ObjectId and timestamps to datetime
            updates = []
            for a_id, ts in article_views.items():
                try:
                    article_obj_id = ObjectId(a_id)
                except Exception:
                    continue  # skip invalid IDs
                updates.append({"article_id": article_obj_id, "timestamp": datetime.fromisoformat(ts)})

            if not updates:
                continue

            # Update MongoDB analytics (store user_id as string, not ObjectId)
            analytics_collection.update_one(
                {"user_id": user_id},  # <---- changed here
                {
                    "$addToSet": {"articles_read_ids": {"$each": [u["article_id"] for u in updates]}},
                    "$push": {"reading_history": {"$each": updates}},
                    "$set": {"last_updated": datetime.utcnow()}
                },
                upsert=True
            )

            # ----------------------
            # Update gamification in Supabase
            # ----------------------
            resp = supabase.table("users").select("gamification").eq("id", user_id).execute()
            if resp.data:
                current_gam = resp.data[0].get("gamification", {"points": 0, "streak": 0})
            else:
                current_gam = {"points": 0, "streak": 0}

            # Increment points by number of new reads
            points_increment = len(updates)
            new_points = current_gam.get("points", 0) + points_increment

            # Update streak: check if last read was yesterday or today
            last_read_ts = None
            if "last_read_date" in current_gam:
                try:
                    last_read_ts = datetime.fromisoformat(current_gam["last_read_date"])
                except Exception:
                    pass

            today = datetime.utcnow().date()
            yesterday = today - timedelta(days=1)
            if last_read_ts and last_read_ts.date() == yesterday:
                new_streak = current_gam.get("streak", 0) + 1
            elif last_read_ts and last_read_ts.date() == today:
                new_streak = current_gam.get("streak", 0)
            else:
                new_streak = 1  # reset streak

            # Prepare updated gamification
            updated_gam = {
                "points": new_points,
                "streak": new_streak,
                "last_read_date": datetime.utcnow().isoformat()
            }

            # Update Supabase
            supabase.table("users").update({"gamification": updated_gam}).eq("id", user_id).execute()

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

        one_week_ago = datetime.utcnow() - timedelta(days=7)
        recent_reads = [
            r for r in analytics_doc.get("reading_history", [])
            if r.get("timestamp") and r["timestamp"] >= one_week_ago
        ]

        return {
            "username": user_data.get("username"),
            "points": gamification.get("points", 0),
            "streak": gamification.get("streak", 0),
            "articles_read_total": len(analytics_doc.get("articles_read_ids", [])),
            "articles_read_last_week": len(recent_reads),
            "vocab_words_added": analytics_doc.get("vocab_added_count", 0),
            "reading_history": analytics_doc.get("reading_history", [])
        }

   
# Singleton instance
analytics_service = AnalyticsService()