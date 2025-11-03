# app/services/scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler
import asyncio
from app.services.news_pipeline import fetch_and_process_feeds

# Expanded RSS feeds list
feeds = [
    "https://www.theguardian.com/world/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.npr.org/1001/rss.xml",
    "https://rss.cnn.com/rss/edition.rss",
    "https://www.reutersagency.com/feed/?best-topics=world",
    "https://www.engadget.com/rss.xml",
    "https://www.wired.com/feed/rss",
    "https://feeds.arstechnica.com/arstechnica/index"
]

def run_asyncio_task(coro):
    """Helper to run asyncio coroutine from APScheduler job"""
    asyncio.run(coro)

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run every 15 minutes
    scheduler.add_job(lambda: run_asyncio_task(fetch_and_process_feeds(feeds)), "interval", minutes=15)
    scheduler.start()
    print(f"Scheduler started: fetching news from {len(feeds)} feeds every 15 minutes")
