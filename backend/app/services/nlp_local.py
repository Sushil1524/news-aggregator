# app/services/nlp_local.py

from transformers import pipeline
from keybert import KeyBERT
import re

sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english"
)

# Faster summarizer with better quality
summarizer = pipeline(
    "summarization", 
    model="sshleifer/distilbart-cnn-12-6",
    device=-1  # CPU
)

# Keyword extraction
kw_model = KeyBERT(model="distilbert-base-nli-mean-tokens")

# Zero-shot classifier for better category detection
category_classifier = pipeline(
    "zero-shot-classification",
    model="facebook/bart-large-mnli",
    device=-1
)

# Comprehensive category definitions
CATEGORY_LABELS = [
    "Technology and Computing",
    "Politics and Government", 
    "Business and Finance",
    "Health and Medicine",
    "Sports and Athletics",
    "Entertainment and Media",
    "Science and Research",
    "Crime and Justice",
    "Education",
    "Environment and Climate",
    "Travel and Tourism",
    "Lifestyle and Culture",
    "Obituary and Death",
    "General News"
]

# Mapping from detailed labels to simple frontend categories
CATEGORY_MAPPING = {
    "Technology and Computing": "Technology",
    "Politics and Government": "Politics",
    "Business and Finance": "Business",
    "Health and Medicine": "Health",
    "Sports and Athletics": "Sports",
    "Entertainment and Media": "Entertainment",
    "Science and Research": "Science",
    "Crime and Justice": "Crime",
    "Education": "Education",
    "Environment and Climate": "Environment",
    "Travel and Tourism": "Travel",
    "Lifestyle and Culture": "Lifestyle",
    "Obituary and Death": "Obituary",
    "General News": "General"
}

# ==============================
# Helper functions
# ==============================

def analyze_sentiment(text: str) -> str:
    """Perform sentiment analysis using BERT model."""
    try:
        result = sentiment_analyzer(text[:512])[0]
        label = result['label'].lower()
        score = result.get('score', 0.0)
        if score < 0.65:
            return "neutral"
        return "positive" if "pos" in label else "negative"
    except Exception as e:
        print(f"Sentiment analysis failed: {e}")
        return "neutral"


def classify_category(text: str) -> str:
    """
    Use zero-shot classification for accurate category detection.
    Falls back to keyword matching if model fails.
    """
    try:
        # Take first 1000 chars for classification (enough context, faster)
        sample = text[:1000]
        
        result = category_classifier(
            sample,
            CATEGORY_LABELS,
            multi_label=False
        )
        
        # Get top prediction
        top_label = result['labels'][0]
        top_score = result['scores'][0]
        
        # If confidence is too low, return General
        if top_score < 0.3:
            return "General"
        
        # Map to frontend category
        return CATEGORY_MAPPING.get(top_label, "General")
        
    except Exception as e:
        print(f"Category classification failed: {e}")
        # Fallback to simple keyword matching
        return fallback_category_classification(text)


def fallback_category_classification(text: str) -> str:
    """Enhanced keyword-based fallback with better patterns."""
    text_lower = text.lower()
    
    # Death/Obituary keywords (high priority)
    death_keywords = [
        r'\bdied\b', r'\bdeath\b', r'\bpassed away\b', r'\bobitu',
        r'\bfuneral\b', r'\bmourning\b', r'\bcondolences\b',
        r'\blate\b.*\b(actor|singer|politician|leader)',
        r'\b(killed|deceased|demise)\b'
    ]
    for pattern in death_keywords:
        if re.search(pattern, text_lower):
            return "Obituary"
    
    # Technology keywords
    tech_keywords = [
        r'\b(tech|software|ai|computer|gadget|smartphone|app|digital)\b',
        r'\b(algorithm|programming|cybersecurity|blockchain|cryptocurrency)\b',
        r'\b(google|apple|microsoft|meta|amazon|tesla|spacex)\b(?!.*\b(stock|shares|market)\b)',
        r'\b(startup|silicon valley|innovation|robotics)\b'
    ]
    tech_count = sum(len(re.findall(p, text_lower)) for p in tech_keywords)
    
    # Politics keywords
    politics_keywords = [
        r'\b(election|government|senate|congress|parliament|minister|president)\b',
        r'\b(policy|legislation|democrat|republican|political|campaign)\b',
        r'\b(vote|ballot|governor|mayor|constituency)\b',
        r'\b(diplomacy|treaty|sanctions|foreign policy)\b'
    ]
    politics_count = sum(len(re.findall(p, text_lower)) for p in politics_keywords)
    
    # Business keywords
    business_keywords = [
        r'\b(market|stock|shares|finance|economy|revenue|profit|loss)\b',
        r'\b(investment|investor|trading|wall street|nasdaq|dow jones)\b',
        r'\b(earnings|quarterly|fiscal|merger|acquisition|ipo)\b',
        r'\b(corporate|company|business|enterprise|startup)\b.*\b(funding|valuation|growth)\b'
    ]
    business_count = sum(len(re.findall(p, text_lower)) for p in business_keywords)
    
    # Health keywords
    health_keywords = [
        r'\b(health|medicine|medical|virus|disease|hospital|clinic)\b',
        r'\b(covid|pandemic|vaccine|drug|treatment|therapy|diagnosis)\b',
        r'\b(doctor|physician|patient|surgery|healthcare)\b',
        r'\b(mental health|wellness|fitness|nutrition)\b'
    ]
    health_count = sum(len(re.findall(p, text_lower)) for p in health_keywords)
    
    # Sports keywords
    sports_keywords = [
        r'\b(football|soccer|basketball|nba|nfl|cricket|tennis|hockey)\b',
        r'\b(olympics|tournament|championship|match|game|player|team)\b',
        r'\b(coach|athlete|score|win|loss|league|season)\b',
        r'\b(world cup|super bowl|wimbledon|formula 1|f1)\b'
    ]
    sports_count = sum(len(re.findall(p, text_lower)) for p in sports_keywords)
    
    # Crime keywords
    crime_keywords = [
        r'\b(crime|criminal|arrest|police|investigation|jail|prison)\b',
        r'\b(murder|robbery|theft|assault|fraud|scam)\b',
        r'\b(court|trial|verdict|sentence|guilty|innocent)\b',
        r'\b(lawsuit|sue|attorney|judge)\b'
    ]
    crime_count = sum(len(re.findall(p, text_lower)) for p in crime_keywords)
    
    # Score and determine category
    scores = {
        "Technology": tech_count,
        "Politics": politics_count,
        "Business": business_count,
        "Health": health_count,
        "Sports": sports_count,
        "Crime": crime_count
    }
    
    max_category = max(scores, key=scores.get)
    if scores[max_category] >= 2:  # Minimum threshold
        return max_category
    
    return "General"


def smart_truncate(text: str, max_length: int = 1024) -> str:
    """
    Intelligently truncate text to fit model limits.
    Prioritizes complete sentences and important content.
    """
    if len(text) <= max_length:
        return text
    
    # Try to cut at sentence boundary
    truncated = text[:max_length]
    last_period = truncated.rfind('.')
    last_question = truncated.rfind('?')
    last_exclamation = truncated.rfind('!')
    
    last_sentence_end = max(last_period, last_question, last_exclamation)
    
    if last_sentence_end > max_length * 0.7:  # At least 70% of desired length
        return text[:last_sentence_end + 1]
    
    return truncated


# ==============================
# Main NLP processing
# ==============================

def process_article_nlp(content: str) -> dict:
    """
    Process article content:
    - Summarization (DistilBART) - improved, faster
    - Sentiment
    - Category (zero-shot classification)
    - Keywords
    """
    
    # --------------------------
    # Summarization (simplified and faster)
    # --------------------------
    try:
        # Clean content
        content_clean = re.sub(r'\s+', ' ', content).strip()
        
        # For very short content, just return it
        if len(content_clean) < 200:
            summary = content_clean
        else:
            # Single-pass summarization with smart truncation
            input_text = smart_truncate(content_clean, max_length=1024)
            
            # Calculate dynamic lengths based on input
            input_length = len(input_text.split())
            max_length = min(150, max(60, input_length // 3))
            min_length = min(40, max_length - 20)
            
            result = summarizer(
                input_text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                truncation=True,
                num_beams=4,  # Reduced from 6 for speed
                early_stopping=True,
                no_repeat_ngram_size=3,
                length_penalty=1.0
            )
            
            summary = result[0]["summary_text"].strip()
            
            # Format into paragraphs for readability
            sentences = re.split(r'(?<=[.!?])\s+', summary)
            if len(sentences) > 3:
                # Group into paragraphs (2-3 sentences each)
                paragraphs = []
                for i in range(0, len(sentences), 2):
                    para = " ".join(sentences[i:i+2])
                    if para:
                        paragraphs.append(para)
                summary = "\n\n".join(paragraphs)
    
    except Exception as e:
        print(f"Summarization failed: {e}")
        # Fallback: return first few sentences
        sentences = re.split(r'(?<=[.!?])\s+', content[:500])
        summary = " ".join(sentences[:3])
    
    # --------------------------
    # Sentiment
    # --------------------------
    sentiment = analyze_sentiment(summary)
    
    # --------------------------
    # Category (using zero-shot classification)
    # --------------------------
    category = classify_category(content)
    
    # --------------------------
    # Keywords
    # --------------------------
    try:
        # Use summary for keywords if content is very long
        keyword_text = summary if len(content) > 2000 else content[:1000]
        tags = kw_model.extract_keywords(
            keyword_text,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=5
        )
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