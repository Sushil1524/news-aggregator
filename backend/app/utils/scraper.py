# app/utils/scraper.py

def scrape_article(url: str):
    """
    Extract main content + image URLs
    """
    import requests
    from bs4 import BeautifulSoup

    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        paragraphs = soup.find_all("p")
        content = "\n".join([p.get_text() for p in paragraphs])

        # Extract first image
        img_tag = soup.find("img")
        image_url = img_tag['src'] if img_tag else None

        return {
            "content": content,
            "image_url": image_url,
            "source_url": url
        }
    except Exception as e:
        print(f"Scraper error: {e}")
        return None
