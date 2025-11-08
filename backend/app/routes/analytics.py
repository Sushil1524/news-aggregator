from fastapi import APIRouter, Depends, HTTPException
from app.services.analytics_service import analytics_service
from app.utils.dependencies import get_current_user  # your existing JWT auth dependency

router = APIRouter()

# -------------------------------
# Public / site-wide analytics
# -------------------------------
@router.get("/trending")
def get_trending_articles(limit: int = 10):
    return analytics_service.get_trending_articles(limit)

@router.get("/top-categories")
def get_top_categories(limit: int = 5):
    return analytics_service.get_top_categories(limit)

@router.get("/daily-counts")
def get_daily_counts(days: int = 7):
    return analytics_service.get_daily_article_counts(days)


# -------------------------------
# User analytics (requires auth)
# -------------------------------
@router.get("/dashboard")
def get_user_dashboard(user=Depends(get_current_user)):
    """
    Fetch the analytics dashboard for the logged-in user.
    Combines Supabase gamification + MongoDB reading history.
    """
    return analytics_service.get_user_dashboard_data(user["id"])