# app/utils/rss_parser.py

import feedparser
from datetime import datetime
import re

def parse_rss_feed(feed_url: str):
    """
    Parses an RSS feed and returns a list of raw articles with images if available.
    """
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries:
        # Try to get image from common RSS fields
        image_url = None
        if "media_content" in entry and len(entry.media_content) > 0:
            image_url = entry.media_content[0].get("url")
        elif "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
            image_url = entry.media_thumbnail[0].get("url")
        elif "enclosures" in entry and len(entry.enclosures) > 0:
            image_url = entry.enclosures[0].get("url")

        # Fallback: extract first <img> tag from content or summary
        if not image_url:
            html_source = (
                entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")
            )
            img_match = re.search(r'<img[^>]+src="([^">]+)"', html_source)
            if img_match:
                image_url = img_match.group(1)

        article = {
            "title": entry.get("title"),
            "url": entry.get("link"),
            "summary": entry.get("summary", ""),
            "content": entry.get("content")[0].value if entry.get("content") else "",
            "published_at": datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else None,
            "source": feed.feed.get("title", ""),
            "tags": [tag.term for tag in entry.get("tags", [])] if entry.get("tags") else [],
            "image_url": image_url  # ✅ Store image with article
        }

        articles.append(article)

    return articles
