from flask import Blueprint, jsonify
from app.utils.auth_decorator import token_required

# --- Placeholder Service ---
class AnalyticsService:
    # MOCK: In-memory data for demonstration
    analytics_data = {
        "user_user_2": {
            "articles_read": 15,
            "vocab_learned": 30,
            "current_streak": 5
        }
    }
    def get_data_for_user(self, user_id):
        # Return default data if user has no analytics yet
        return self.analytics_data.get(user_id, {
            "articles_read": 0,
            "vocab_learned": 0,
            "current_streak": 0
        })

analytics_service = AnalyticsService()
# --- End Placeholder ---

user = Blueprint('user', __name__)

# Note: a general /profile route is now in auth_routes.py to be closer to the auth logic
# This file will focus on user-specific features like analytics.

@user.route('/analytics', methods=['GET'])
@token_required
def get_analytics(current_user):
    """
    Endpoint to fetch the user's personal analytics dashboard data.
    Requires user to be authenticated.
    """
    try:
        user_id = current_user['id']
        data = analytics_service.get_data_for_user(user_id)
        return jsonify({"analytics": data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

