from app.core.db import mongo
from bson.objectid import ObjectId
import datetime

class AnalyticsService:
    def get_user_dashboard_data(self, user_id):
        """
        Retrieves and computes the analytics data for a user's dashboard.
        """
        # Fetch the user's core profile for gamification stats
        user_profile = mongo.db.users.find_one(
            {'_id': ObjectId(user_id)},
            {'gamification': 1, 'username': 1} # Projection
        )
        
        # Fetch the user's analytics document
        analytics_data = mongo.db.analytics.find_one({'user_id': ObjectId(user_id)})
        
        if not user_profile:
            raise ValueError("User not found")
        
        if not analytics_data:
            # If no analytics doc exists, return defaults from the user profile
            return {
                "username": user_profile.get('username'),
                "points": user_profile.get('gamification', {}).get('points', 0),
                "streak": user_profile.get('gamification', {}).get('streak', 0),
                "articles_read": 0,
                "vocab_words_added": 0,
                "reading_history": []
            }
            
        # Combine data from both sources
        dashboard_view = {
            "username": user_profile.get('username'),
            "points": user_profile.get('gamification', {}).get('points', 0),
            "streak": user_profile.get('gamification', {}).get('streak', 0),
            "articles_read": len(analytics_data.get('articles_read_ids', [])),
            "vocab_words_added": analytics_data.get('vocab_added_count', 0),
            "reading_history": analytics_data.get('daily_reading_history', [])
        }
        
        return dashboard_view

    def track_article_read(self, user_id, article_id):
        """
        Tracks that a user has read an article.
        Creates an analytics document if one doesn't exist.
        """
        user_oid = ObjectId(user_id)
        article_oid = ObjectId(article_id)
        
        # Use upsert=True to create the document if it doesn't exist
        mongo.db.analytics.update_one(
            {'user_id': user_oid},
            {
                '$addToSet': {'articles_read_ids': article_oid}, # Prevents duplicate article IDs
                '$set': {'last_updated': datetime.datetime.now(datetime.timezone.utc)}
            },
            upsert=True
        )
        
        # You would also add logic here to update points and streaks in the 'users' collection
        # For simplicity, that is omitted here but would be part of a complete implementation.
        
        return True

# Instantiate the service
analytics_service = AnalyticsService()
