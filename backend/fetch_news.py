from app.services.news_service import fetch_and_store_rss

feeds = [
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml"
]

for feed in feeds:
    stored = fetch_and_store_rss(feed)
    print(f"Stored {len(stored)} new articles from {feed}")
