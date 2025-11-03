import asyncio
from datetime import datetime
# from app.services.news_service import scrape_article
from app.utils.scraper import scrape_article
from app.utils.rss_parser import parse_rss_feed
from app.services.nlp_local import analyze_sentiment, process_article_nlp
from app.config.mongo import (
    raw_articles_collection,
    articles_collection,
    pipeline_logs_collection,
    feeds_metadata_collection
)
from asyncio import Semaphore

MAX_CONCURRENT = 5
semaphore = Semaphore(MAX_CONCURRENT)

# Batch size for Gemini (max 10 per free tier)
BATCH_SIZE = 10
# Throttle between batches (seconds)
BATCH_THROTTLE = 6


async def process_raw_article(raw_article):
    if articles_collection.find_one({"url": raw_article["url"]}):
        return None

    scraped = await asyncio.to_thread(scrape_article, raw_article["url"])
    if not scraped or not scraped.get("content"):
        return None

    raw_article["content"] = scraped["content"]
    raw_article["image_url"] = scraped.get("image_url")
    raw_article["source_url"] = raw_article["url"]

    # Process locally instead of Gemini
    processed = await asyncio.to_thread(process_article_nlp, raw_article["content"])

    structured_article = {
        "title": raw_article["title"],
        "url": raw_article["url"],
        "summary": processed["summary"],
        "content": processed["synthesized_content"],
        "category": processed["category"],
        "tags": processed["tags"],
        "sentiment": processed["sentiment"],
        "author_email": "system",
        "image_url": raw_article.get("image_url"),
        "source_url": raw_article.get("source_url"),
        "upvotes": 0,
        "downvotes": 0,
        "comments_count": 0,
        "views": 0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    try:
        articles_collection.insert_one(structured_article)
        print(f"Processed article: {raw_article['title']}")
    except Exception as e:
        print(f"Failed to insert article {raw_article['url']}: {e}")

    return structured_article

async def fetch_and_process_feeds(feeds: list):
    """
    Always refetch all RSS feed items, but process only new ones.
    Updates feed metadata with latest fetched timestamp every run.
    """
    total_fetched = 0
    total_processed = 0
    nlp_success = 0
    nlp_fail = 0

    tasks = []

    for feed_url in feeds:
        try:
            print(f"🔄 Fetching feed: {feed_url}")

            # Always refetch full feed
            raw_articles = parse_rss_feed(feed_url)
            total_fetched += len(raw_articles)

            new_articles = []

            for article in raw_articles:
                # Skip if article already exists (by URL)
                if raw_articles_collection.find_one({"url": article["url"]}):
                    continue

                article["created_at"] = datetime.utcnow()
                raw_articles_collection.insert_one(article)
                new_articles.append(article)
                tasks.append(process_raw_article(article))

            # ✅ Always update last_fetched, even if no new articles
            feeds_metadata_collection.update_one(
                {"feed_url": feed_url},
                {"$set": {"last_fetched": datetime.utcnow()}},
                upsert=True
            )

            print(f"✅ {len(new_articles)} new articles queued for processing from {feed_url}")

        except Exception as e:
            print(f"❌ Error processing feed {feed_url}: {e}")

    # Run all NLP processing tasks concurrently
    if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            total_processed += 1
            if r is None or isinstance(r, Exception):
                nlp_fail += 1
            else:
                nlp_success += 1
    else:
        results = []

    # Log this pipeline run
    pipeline_logs_collection.insert_one({
        "timestamp": datetime.utcnow(),
        "fetched": total_fetched,
        "processed": total_processed,
        "nlp_success": nlp_success,
        "nlp_fail": nlp_fail
    })

    print(
        f"📊 Pipeline run summary — fetched={total_fetched}, "
        f"processed={total_processed}, nlp_success={nlp_success}, nlp_fail={nlp_fail}"
    )

    return results
