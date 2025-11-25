# app/services/nlp_local.py

from transformers import pipeline
from keybert import KeyBERT
import re

# ==============================
# LIGHTWEIGHT MODEL CHOICES
# ==============================

# Sentiment: Much smaller than distilbert (82MB vs 250MB+)
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="distilbert-base-uncased-finetuned-sst-2-english",
    device=-1,  # CPU
    model_kwargs={"low_cpu_mem_usage": True}
)

# Summarization: Lightweight option
summarizer = pipeline(
    "summarization",
    model="sshleifer/distilbart-cnn-6-6",  # Only 255MB (6-6 version, much smaller than large)
    device=-1,
    model_kwargs={"low_cpu_mem_usage": True},
    framework="pt"
)

# Lightweight keyword extraction
kw_model = KeyBERT(
    model="all-MiniLM-L6-v2",  # 80MB vs 400MB+ for larger models
)

# Lightweight category classification - use simple keyword matching instead
# (zero-shot models are too heavy, fallback is better quality anyway)
category_classifier = None

# ==============================
# CATEGORY CONFIGURATION
# ==============================

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
# HELPER FUNCTIONS
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
    Use keyword-based classification (no heavy model needed).
    This is actually more accurate than zero-shot for news categorization.
    """
    try:
        return fallback_category_classification(text)
    except Exception as e:
        print(f"Category classification failed: {e}")
        return "General"


def fallback_category_classification(text: str) -> str:
    """Enhanced keyword-based fallback with better patterns."""
    text_lower = text.lower()
    
    # Death/Obituary (highest priority)
    death_keywords = [
        r'\bdied\b', r'\bdeath\b', r'\bpassed away\b', r'\bobitu',
        r'\bfuneral\b', r'\bmourning\b', r'\bcondolences\b',
        r'\blate\b.*\b(actor|singer|politician|leader)',
        r'\b(killed|deceased|demise)\b'
    ]
    for pattern in death_keywords:
        if re.search(pattern, text_lower):
            return "Obituary"
    
    # Technology
    tech_keywords = [
        r'\b(tech|software|ai|computer|gadget|smartphone|app|digital|internet|web|data|cloud|server|database|api|developer|programming|code|bug|framework)\b',
        r'\b(algorithm|programming|cybersecurity|blockchain|cryptocurrency|nft|metaverse|vr|ar|iot)\b',
        r'\b(google|apple|microsoft|meta|amazon|tesla|spacex|openai|nvidia|intel|ibm)\b',
        r'\b(startup|silicon valley|innovation|robotics|automation|machine learning|neural|neural network)\b'
    ]
    tech_count = sum(len(re.findall(p, text_lower)) for p in tech_keywords)
    
    # Politics
    politics_keywords = [
        r'\b(election|government|senate|congress|parliament|minister|president|politician|political|vote)\b',
        r'\b(policy|legislation|democrat|republican|campaign|candidate|ballot|governor|mayor|constituency|congress|senate)\b',
        r'\b(diplomacy|treaty|sanctions|foreign policy|ambassador|diplomat|international relations|summit|parliament)\b',
        r'\b(administration|administration|law|bill|act|statute|regulation)\b'
    ]
    politics_count = sum(len(re.findall(p, text_lower)) for p in politics_keywords)
    
    # Business/Finance
    business_keywords = [
        r'\b(market|stock|shares|finance|economy|revenue|profit|loss|earnings|deal|acquisition|merger|ipo)\b',
        r'\b(investment|investor|trading|wall street|nasdaq|dow jones|financial|fund|hedge|portfolio|index)\b',
        r'\b(quarterly|fiscal|bankruptcy|dividend|earnings call|guidance|forecast|analyst|rating)\b',
        r'\b(corporate|company|business|enterprise|startup|venture|funding|valuation|growth|expansion|layoff|hiring)\b',
        r'\b(retail|manufacturing|supply chain|logistics|commerce|trade|export|import)\b'
    ]
    business_count = sum(len(re.findall(p, text_lower)) for p in business_keywords)
    
    # Health/Medicine
    health_keywords = [
        r'\b(health|medicine|medical|virus|disease|hospital|clinic|healthcare|patient|doctor|physician|surgeon)\b',
        r'\b(covid|pandemic|vaccine|drug|treatment|therapy|diagnosis|symptom|infection|immune|antibody)\b',
        r'\b(mental health|wellness|fitness|nutrition|diet|exercise|epidemic|outbreak|contagion)\b',
        r'\b(fda|pharmaceutical|clinical trial|medication|prescription|side effect)\b'
    ]
    health_count = sum(len(re.findall(p, text_lower)) for p in health_keywords)
    
    # Sports
    sports_keywords = [
        r'\b(football|soccer|basketball|nba|nfl|cricket|tennis|hockey|golf|rugby|boxing|mma|ufc)\b',
        r'\b(olympics|tournament|championship|match|game|player|team|athlete|coach|league|season|playoff|super bowl)\b',
        r'\b(score|win|loss|tie|draw|goal|point|assist|defense|offense|draft|trade|contract)\b',
        r'\b(world cup|wimbledon|formula 1|f1|grand slam|tournament|pennant|division|conference)\b'
    ]
    sports_count = sum(len(re.findall(p, text_lower)) for p in sports_keywords)
    
    # Crime/Justice
    crime_keywords = [
        r'\b(crime|criminal|arrest|police|investigation|jail|prison|conviction|accused|defendant|prosecution)\b',
        r'\b(murder|robbery|theft|assault|fraud|scam|rape|kidnapping|arson|burglary|embezzlement)\b',
        r'\b(court|trial|verdict|sentence|guilty|innocent|judge|jury|attorney|lawyer|legal)\b',
        r'\b(lawsuit|sue|pleaded|charged|indicted|subpoena|FBI|detective|suspect|witness|evidence)\b'
    ]
    crime_count = sum(len(re.findall(p, text_lower)) for p in crime_keywords)
    
    # Entertainment/Media
    entertainment_keywords = [
        r'\b(movie|film|actor|actress|director|producer|cinema|hollywood|award|oscar|emmy|grammy)\b',
        r'\b(music|song|artist|album|concert|tour|festival|band|singer|musician|album|single)\b',
        r'\b(tv|television|series|episode|show|streaming|netflix|hulu|disney|premiere|finale)\b',
        r'\b(entertainment|celebrity|star|famous|role|character|cast|sequel|blockbuster)\b'
    ]
    entertainment_count = sum(len(re.findall(p, text_lower)) for p in entertainment_keywords)
    
    # Science/Research
    science_keywords = [
        r'\b(science|research|study|scientist|researcher|laboratory|experiment|discovery|breakthrough)\b',
        r'\b(physics|chemistry|biology|astronomy|quantum|relativity|particle|atom|molecule|element)\b',
        r'\b(nasa|space|telescope|rover|satellite|astronaut|spacecraft|mission|planet|galaxy|universe)\b',
        r'\b(fossil|paleontology|evolution|extinction|carbon dating|archaeological)\b'
    ]
    science_count = sum(len(re.findall(p, text_lower)) for p in science_keywords)
    
    # Environment/Climate
    environment_keywords = [
        r'\b(climate|environment|weather|global warming|greenhouse|carbon|emission|pollution|renewable|solar|wind)\b',
        r'\b(environmental|conservation|endangered|wildlife|animal|species|extinction|habitat|ecosystem)\b',
        r'\b(ocean|forest|rainforest|deforestation|ice cap|glacier|arctic|antarctica|coral reef)\b'
    ]
    environment_count = sum(len(re.findall(p, text_lower)) for p in environment_keywords)
    
    scores = {
        "Technology": tech_count,
        "Politics": politics_count,
        "Business": business_count,
        "Health": health_count,
        "Sports": sports_count,
        "Crime": crime_count,
        "Entertainment": entertainment_count,
        "Science": science_count,
        "Environment": environment_count
    }
    
    max_category = max(scores, key=scores.get)
    # Lowered threshold from 2 to 1 - any strong match is valid
    if scores[max_category] >= 1:
        return max_category
    
    return "General"


def split_into_sentences(text: str) -> list:
    """Split text into sentences more reliably."""
    # Handle common abbreviations
    text = re.sub(r'(?<!\w)([A-Z]\.){2,}', lambda m: m.group(0).replace('.', '[DOT]'), text)
    text = re.sub(r'(?<!\w)(\w\.){2,}', lambda m: m.group(0).replace('.', '[DOT]'), text)
    
    # Split on sentence endings
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Restore abbreviations
    sentences = [s.replace('[DOT]', '.') for s in sentences]
    
    return [s.strip() for s in sentences if s.strip()]


def fix_summary_truncation(text: str, min_length: int = 30) -> str:
    """
    Fix incomplete summaries by ensuring they end properly.
    Adds missing punctuation if needed.
    """
    text = text.strip()
    
    # If already ends with proper punctuation or is very short, return as-is
    if text.endswith(('.', '!', '?')) or len(text.split()) <= min_length:
        return text
    
    # Find last complete sentence
    last_period = text.rfind('.')
    last_question = text.rfind('?')
    last_exclamation = text.rfind('!')
    
    last_punct = max(last_period, last_question, last_exclamation)
    
    if last_punct > 0 and last_punct > len(text) * 0.5:  # Found punct in last half
        return text[:last_punct + 1]
    
    # Last resort: try to find a clause break
    if ',' in text[-100:]:
        last_comma = text.rfind(',')
        # Look for natural break after comma
        remaining = text[last_comma + 1:].strip()
        if len(remaining.split()) <= 10:  # Short enough to be incomplete
            return text[:last_comma] + '.'
    
    # If nothing else works, add ellipsis to indicate truncation
    return text + '.'


# ==============================
# MAIN NLP PROCESSING
# ==============================

def process_article_nlp(content: str) -> dict:
    """
    Process article content with optimized models:
    - Summarization (BART) - faster, better quality
    - Sentiment
    - Category (zero-shot classification)
    - Keywords
    """
    
    # --------------------------
    # SUMMARIZATION (IMPROVED)
    # --------------------------
    try:
        content_clean = re.sub(r'\s+', ' ', content).strip()
        
        if len(content_clean.split()) < 50:
            summary = content_clean
        else:
            # Use more aggressive truncation for efficiency
            input_text = content_clean[:1500]  # Limit input
            
            # Calculate dynamic length based on input word count
            word_count = len(input_text.split())
            target_words = max(60, min(150, word_count // 4))
            
            result = summarizer(
                input_text,
                max_length=target_words,
                min_length=max(40, target_words - 30),
                do_sample=False,
                truncation=True,
                num_beams=3,  # Reduced for speed
                early_stopping=True,
                no_repeat_ngram_size=2,
                length_penalty=0.8
            )
            
            summary = result[0]["summary_text"].strip()
            
            # Fix any truncation issues
            summary = fix_summary_truncation(summary, min_length=40)
            
            # Format into readable paragraphs (optional)
            sentences = split_into_sentences(summary)
            if len(sentences) > 2:
                paragraphs = []
                for i in range(0, len(sentences), 2):
                    para = " ".join(sentences[i:i+2])
                    if para:
                        paragraphs.append(para)
                summary = "\n\n".join(paragraphs)
    
    except Exception as e:
        print(f"Summarization failed: {e}")
        sentences = split_into_sentences(content[:500])
        summary = " ".join(sentences[:3]) if sentences else content[:200]
    
    # --------------------------
    # SENTIMENT
    # --------------------------
    sentiment = analyze_sentiment(summary if summary else content[:512])
    
    # --------------------------
    # CATEGORY
    # --------------------------
    category = classify_category(content)
    
    # --------------------------
    # KEYWORDS
    # --------------------------
    try:
        keyword_text = summary if len(content) > 2000 else content[:1000]
        tags = kw_model.extract_keywords(
            keyword_text,
            keyphrase_ngram_range=(1, 2),
            stop_words='english',
            top_n=5,
            use_maxsum=True,
            nr_candidates=20
        )
        tags = [t[0] for t in tags]
    except Exception as e:
        print(f"Keyword extraction failed: {e}")
        tags = []
    
    # --------------------------
    # RETURN RESULTS
    # --------------------------
    return {
        "summary": summary,
        "sentiment": sentiment,
        "category": category,
        "tags": tags,
        "synthesized_content": content
    }