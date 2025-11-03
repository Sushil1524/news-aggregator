# app/utils/rss_parser.py

import feedparser
from datetime import datetime

def parse_rss_feed(feed_url: str):
    """
    Parses an RSS feed and returns a list of raw articles
    """
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries:
        article = {
            "title": entry.get("title"),
            "url": entry.get("link"),
            "summary": entry.get("summary", ""),
            "content": entry.get("content")[0].value if entry.get("content") else "",
            "published_at": datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else None,
            "source": feed.feed.get("title", ""),
            "tags": [tag.term for tag in entry.get("tags", [])] if entry.get("tags") else []
        }
        articles.append(article)
    return articles
