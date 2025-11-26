import feedparser
import re
from datetime import datetime
from bs4 import BeautifulSoup

def parse_rss_feed(feed_url: str):
    print(f"Parsing {feed_url}...")
    feed = feedparser.parse(feed_url)
    articles = []

    for entry in feed.entries[:3]: # Check first 3 entries
        image_url = None
        # User's logic
        if "media_content" in entry and len(entry.media_content) > 0:
            image_url = entry.media_content[0].get("url")
        elif "media_thumbnail" in entry and len(entry.media_thumbnail) > 0:
            image_url = entry.media_thumbnail[0].get("url")
        elif "enclosures" in entry and len(entry.enclosures) > 0:
            image_url = entry.enclosures[0].get("url")

        if not image_url:
            html_source = (
                entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")
            )
            # Try regex
            img_match = re.search(r'<img[^>]+src="([^">]+)"', html_source)
            if img_match:
                image_url = img_match.group(1)
            
            # Try BeautifulSoup
            if not image_url and html_source:
                soup = BeautifulSoup(html_source, 'html.parser')
                img = soup.find('img')
                if img and img.get('src'):
                    image_url = img.get('src')
                    print(f"  Found image via BeautifulSoup: {image_url}")

        print(f"  Title: {entry.get('title')}")
        print(f"  Image: {image_url}")
        if not image_url:
            print("  Keys:", entry.keys())
            if 'media_content' in entry: print("  media_content:", entry.media_content)
            if 'media_thumbnail' in entry: print("  media_thumbnail:", entry.media_thumbnail)
            if 'links' in entry: print("  links:", entry.links)
        print("-" * 20)

urls = [
    "https://www.theguardian.com/world/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.thehindu.com/news/international/feeder/default.rss",
]

for url in urls:
    try:
        parse_rss_feed(url)
    except Exception as e:
        print(f"Error parsing {url}: {e}")
