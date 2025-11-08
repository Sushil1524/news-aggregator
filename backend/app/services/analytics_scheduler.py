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
    scheduler.add_job(flush_views_to_db, "interval", minutes=1, id="flush_views_job")
    print("article views updated")
    # --------------------------
    # Flush user reads every 10 minutes
    # --------------------------
    scheduler.add_job(analytics_service.flush_user_reads, "interval", minutes=1, id="flush_user_reads_job")
    print("user views updated")
    # Start the scheduler
    scheduler.start()
    print("Analytics flusher scheduler started: flushing Redis views and user reads periodically")
