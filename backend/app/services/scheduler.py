# app/services/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from app.services.news_pipeline import fetch_and_process_feeds
from app.services.vocab_scheduler import refresh_daily_vocab
from os

NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY")
# Expanded RSS feeds list
feeds = [
    "https://www.theguardian.com/world/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.arstechnica.com/arstechnica/index"
    "https://www.thehindu.com/news/international/feeder/default.rss",
    # add indian sources
]

def run_asyncio_task(coro):
    """Helper to run asyncio coroutine from APScheduler job"""
    asyncio.run(coro)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every 15 minutes
    scheduler.add_job(refresh_daily_vocab, "cron", hour=5, minute=0)
    print("Scheduler started: refreshing daily vocab at 5:00 AM daily")
    scheduler.add_job(lambda: run_asyncio_task(fetch_and_process_feeds(feeds)), "interval", minutes=15)
    
    # NewsData.io job (every 30 minutes to save API credits)
    # Using the provided API key
    from app.services.news_pipeline import fetch_and_process_newsdata
    scheduler.add_job(lambda: run_asyncio_task(fetch_and_process_newsdata(NEWSDATA_API_KEY)), "interval", minutes=30)
    
    print(f"Scheduler started: fetching news from {len(feeds)} feeds every 15 minutes")
    print("Scheduler started: fetching breaking news from NewsData.io every 30 minutes")
    scheduler.start()
