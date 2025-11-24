# app/services/analytics_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
from app.services.views_service import flush_views_to_db
from app.services.analytics_service import analytics_service

def start_flusher_scheduler():
    """
    Starts the background scheduler to periodically flush
    article views and user read data from Redis to MongoDB.
    """
    scheduler = BackgroundScheduler()

    # --------------------------
    # Flush article views every 5 minutes
    # --------------------------
    scheduler.add_job(flush_views_to_db, "interval", minutes=5, id="flush_views_job")
    # --------------------------
    # Flush user reads every 10 minutes
    # --------------------------
    scheduler.add_job(analytics_service.flush_user_reads, "interval", minutes=10, id="flush_user_reads_job")
    # Start the scheduler
    scheduler.start()
    print("Analytics flusher scheduler started: flushing Redis views and user reads periodically")
