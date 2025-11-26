import sys
import os

# Add the current directory to sys.path to make app.utils.rss_parser importable
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from utils.rss_parser import parse_rss_feed

def test_feed(url):
    print(f"Testing feed: {url}")
    try:
        articles = parse_rss_feed(url)
        print(f"Found {len(articles)} articles.")
        for i, article in enumerate(articles[:3]):
            print(f"Article {i+1}:")
            print(f"  Title: {article.get('title')}")
            print(f"  Image URL: {article.get('image_url')}")
            print("-" * 20)
    except Exception as e:
        print(f"Error parsing feed: {e}")
    print("=" * 40)

if __name__ == "__main__":
    feeds = [
        "https://www.theguardian.com/world/rss",
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.thehindu.com/news/international/feeder/default.rss",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
        "http://feeds.bbci.co.uk/news/technology/rss.xml",
        "https://techcrunch.com/feed/",
    ]

    with open('reproduce_output.txt', 'w', encoding='utf-8') as f:
        for feed in feeds:
            f.write(f"Testing feed: {feed}\n")
            try:
                articles = parse_rss_feed(feed)
                f.write(f"Found {len(articles)} articles.\n")
                if "techcrunch" in feed:
                     import feedparser
                     d = feedparser.parse(feed)
                     if d.entries:
                         f.write(f"TechCrunch Keys: {d.entries[0].keys()}\n")
                         if 'media_content' in d.entries[0]:
                             f.write(f"Media Content: {d.entries[0].media_content}\n")
                for i, article in enumerate(articles[:3]):
                    f.write(f"Article {i+1}:\n")
                    f.write(f"  Title: {article.get('title')}\n")
                    f.write(f"  Image URL: {article.get('image_url')}\n")
                    f.write("-" * 20 + "\n")
            except Exception as e:
                f.write(f"Error parsing feed: {e}\n")
            f.write("=" * 40 + "\n")
