# app/services/nlp_local.py

from transformers import pipeline
from keybert import KeyBERT

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="nlptown/bert-base-multilingual-uncased-sentiment"
)

# Summarizer (can use a small model like t5-small for speed)
summarizer = pipeline("summarization", 
                    #   model="t5-small"
                        model="sshleifer/distilbart-cnn-12-6"
                      )

# Keyword extraction (simple, spaCy or KeyBERT)
kw_model = KeyBERT(model="distilbert-base-nli-mean-tokens")

# Optional: simple rule-based category classification
CATEGORIES = {
    "Technology": ["tech", "software", "AI", "computer", "gadgets"],
    "Politics": ["election", "government", "senate", "policy"],
    "Business": ["market", "stock", "finance", "economy"],
    "Health": ["health", "medicine", "virus", "covid"],
    "Sports": ["football", "soccer", "NBA", "Olympics"]
}

# ==============================
# Helper functions
# ==============================
def analyze_sentiment(text: str) -> str:
    """Perform sentiment analysis using BERT model."""
    try:
        result = sentiment_analyzer(text[:512])[0]
        label = result['label'].lower()
        if "1" in label or "2" in label:
            return "negative"
        elif "3" in label:
            return "neutral"
        else:
            return "positive"
    except Exception as e:
        print(f"Sentiment analysis failed: {e}")
        return "neutral"


def classify_category(text: str) -> str:
    """Rule-based category assignment."""
    text_lower = text.lower()
    for cat, keywords in CATEGORIES.items():
        if any(k in text_lower for k in keywords):
            return cat
    return "General"

def chunk_text(text: str, max_chars: int = 3000):
    """Yield chunks of text, approx safe for 512-token input."""
    for i in range(0, len(text), max_chars):
        yield text[i:i+max_chars]

# ==============================
# Main NLP processing
# ==============================
def process_article_nlp(content: str) -> dict:
    """
    Process article content:
    - Summarization (DistilBART)
    - Sentiment
    - Category
    - Keywords
    """
    # --------------------------
    # Summarization (with chunking)
    # --------------------------
    try:
        summaries = []
        for chunk in chunk_text(content):
            result = summarizer(
                chunk,
                max_length=90,
                min_length=40,
                do_sample=False
            )
            summaries.append(result[0]["summary_text"])
        summary = " ".join(summaries)
    except Exception as e:
        print(f"Summarization failed: {e}")
        summary = content[:200]  # fallback: first 200 chars

# --------------------------
    # Sentiment
    # --------------------------
    sentiment = analyze_sentiment(summary)

    # --------------------------
    # Category
    # --------------------------
    category = classify_category(content)

    # --------------------------
    # Keywords
    # --------------------------
    try:
        tags = kw_model.extract_keywords(content, top_n=5)
        tags = [t[0] for t in tags]
    except Exception as e:
        print(f"Keyword extraction failed: {e}")
        tags = []

# --------------------------
    # Return structured NLP info
    # --------------------------
    return {
        "summary": summary,
        "sentiment": sentiment,
        "category": category,
        "tags": tags,
        "synthesized_content": content  # original content
    }
