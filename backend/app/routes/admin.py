# app/routes/admin.py
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.concurrency import run_in_threadpool
from app.services.news_pipeline import fetch_and_process_feeds, process_raw_article
from app.services.vocab_scheduler import refresh_daily_vocab
from app.config.mongo import raw_articles_collection, articles_collection
from app.utils.dependencies import get_current_admin
from app.config.mongo import db
import asyncio

router = APIRouter()

# Expanded RSS feeds list (same as scheduler.py)
FEEDS = [
    "https://www.theguardian.com/world/rss",
    # "https://www.thehindu.com/news/international/feeder/default.rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.arstechnica.com/arstechnica/index"
]

@router.post("/refresh")
async def manual_refresh(user=Depends(get_current_admin)):
    """
    Manually trigger the news pipeline to fetch latest articles from all feeds.
    Only new articles since last fetch will be processed.
    """
    # refresh_daily_vocab()
    # return {"detail": "Daily vocab refresh triggered"}
    results = await fetch_and_process_feeds(FEEDS)
    processed_count = len([r for r in results if r])
    return {"detail": "Pipeline triggered", "processed_articles": processed_count}

# @router.post("/refresh")
# async def manual_refresh(
#     batch_size: int = Query(10, ge=1, le=100, description="Number of raw articles to process per batch"),
#     user=Depends(get_current_admin)
# ):
#     """
#     Process raw articles stored in MongoDB (PyMongo) in batches.
#     Runs DB + processing inside a threadpool for async compatibility.
#     """
#     raw_articles_col = db["raw_articles"]

#     # Get unprocessed raw articles (sync Mongo query)
#     raw_articles = await run_in_threadpool(
#         lambda: list(raw_articles_col.find({"processed": {"$ne": True}}).limit(batch_size))
#     )

#     if not raw_articles:
#         return {"detail": "No unprocessed raw articles found."}

#     processed_count = 0

#     for article in raw_articles:
#         try:
#             # Await async processing
#             result = await process_raw_article(article)
#             if result:
#                 # Update Mongo synchronously, in threadpool
#                 await run_in_threadpool(
#                     lambda: raw_articles_col.update_one(
#                         {"_id": article["_id"]},
#                         {"$set": {"processed": True, "processed_at": datetime.utcnow()}}
#                     )
#                 )
#                 processed_count += 1
#         except Exception as e:
#             print(f"[Manual Refresh] Error processing article {article.get('_id')}: {e}")

#     return {
#         "detail": "Batch processed successfully",
#         "processed_articles": processed_count,
#         "batch_size": batch_size
#     }