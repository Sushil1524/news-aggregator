# app/routes/admin.py
from fastapi import APIRouter, Depends
from app.services.news_pipeline import fetch_and_process_feeds, process_raw_article
from app.config.mongo import raw_articles_collection, articles_collection
from app.utils.dependencies import get_current_admin
import asyncio

router = APIRouter()

# Expanded RSS feeds list (same as scheduler.py)
FEEDS = [
    "https://www.wired.com/feed/rss",
    "https://www.theguardian.com/world/rss",
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.npr.org/1001/rss.xml",
    "https://rss.cnn.com/rss/edition.rss",
    "https://www.reutersagency.com/feed/?best-topics=world",
    "https://www.engadget.com/rss.xml",
    "https://feeds.arstechnica.com/arstechnica/index"
]

@router.post("/refresh")
async def manual_refresh(user=Depends(get_current_admin)):
    """
    Manually trigger the news pipeline to fetch latest articles from all feeds.
    Only new articles since last fetch will be processed.
    """
    results = await fetch_and_process_feeds(FEEDS)
    processed_count = len([r for r in results if r])
    return {"detail": "Pipeline triggered", "processed_articles": processed_count}
