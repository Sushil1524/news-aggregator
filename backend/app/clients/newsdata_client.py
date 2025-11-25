import requests
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class NewsDataClient:
    BASE_URL = "https://newsdata.io/api/1/news"
    
    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_breaking_news(self, category: str = "technology", language: str = "en", country: str = "us") -> List[Dict[str, Any]]:
        """
        Fetches breaking news from NewsData.io.
        """
        params = {
            "apikey": self.api_key,
            "category": category,
            "language": language,
            "country": country,
            "image": 1 # Request articles with images
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "success":
                logger.error(f"NewsData API error: {data.get('results', 'Unknown error')}")
                return []

            results = data.get("results", [])
            logger.info(f"Fetched {len(results)} articles from NewsData.io")
            return self._map_to_articles(results)

        except requests.RequestException as e:
            logger.error(f"Failed to fetch from NewsData.io: {e}")
            return []

    def _map_to_articles(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        articles = []
        for item in results:
            try:
                # Skip if no image (optional, but user specifically asked for pictures)
                if not item.get("image_url"):
                    continue

                article = {
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "content": item.get("content") or item.get("description") or "",
                    "summary": item.get("description") or "",
                    "image_url": item.get("image_url"),
                    "author_email": "newsdata_bot@intellinews.com", # Placeholder
                    "source_url": item.get("link"),
                    "category": item.get("category", ["general"])[0] if isinstance(item.get("category"), list) else "general",
                    "tags": item.get("keywords") or [],
                    "created_at": self._parse_date(item.get("pubDate")),
                    "updated_at": datetime.utcnow().isoformat(),
                    "upvotes": 0,
                    "downvotes": 0,
                    "comments_count": 0,
                    "views": 0
                }
                articles.append(article)
            except Exception as e:
                logger.warning(f"Error processing NewsData item: {e}")
                continue
        
        return articles

    def _parse_date(self, date_str: Optional[str]) -> str:
        if not date_str:
            return datetime.utcnow().isoformat()
        try:
            # NewsData format example: "2023-10-27 10:00:00" or similar
            # Adjust parsing as needed. If it fails, return now.
            # It seems they use "2023-11-25 12:34:56"
            return date_str # It might be already in a usable string format, or need parsing
        except:
            return datetime.utcnow().isoformat()
