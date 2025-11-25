# app/utils/rss_parser.py

import feedparser
from datetime import datetime
import re

from bs4 import BeautifulSoup

def parse_rss_feed(feed_url: str):
    """
    Parses an RSS feed and returns a list of raw articles with images if available.
    """
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries:
        image_url = None
        
        # 1. Try media_content (often has width/height/bitrate)
        if "media_content" in entry:
            # Sort by width (descending) to get best quality
            # Some feeds might not have width, so handle gracefully
            media_candidates = []
            for m in entry.media_content:
                if m.get("medium") == "image" or m.get("type", "").startswith("image/"):
                    width = int(m.get("width", 0))
                    media_candidates.append((width, m.get("url")))
            
            if media_candidates:
                media_candidates.sort(key=lambda x: x[0], reverse=True)
                image_url = media_candidates[0][1]

        # 2. Try media_thumbnail if no image yet
        if not image_url and "media_thumbnail" in entry:
            # Similar sorting if multiple thumbnails exist
            thumbs = []
            for t in entry.media_thumbnail:
                 width = int(t.get("width", 0))
                 thumbs.append((width, t.get("url")))
            if thumbs:
                thumbs.sort(key=lambda x: x[0], reverse=True)
                image_url = thumbs[0][1]

        # 3. Try enclosures
        if not image_url and "enclosures" in entry:
            for enc in entry.enclosures:
                if enc.get("type", "").startswith("image/"):
                    image_url = enc.get("url")
                    break

        # 4. Fallback: BeautifulSoup on content/summary
        if not image_url:
            html_source = (
                entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")
            )
            if html_source:
                soup = BeautifulSoup(html_source, "html.parser")
                img_tag = soup.find("img")
                if img_tag and img_tag.get("src"):
                    image_url = img_tag["src"]

        article = {
            "title": entry.get("title"),
            "url": entry.get("link"),
            "summary": entry.get("summary", ""),
            "content": entry.get("content")[0].value if entry.get("content") else "",
            "published_at": datetime(*entry.published_parsed[:6]) if entry.get("published_parsed") else None,
            "source": feed.feed.get("title", ""),
            "tags": [tag.term for tag in entry.get("tags", [])] if entry.get("tags") else [],
            "image_url": image_url
        }

        articles.append(article)

    return articles
