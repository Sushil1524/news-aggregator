# app/services/vocab_service.py

from typing import List, Dict, Any, Optional
from datetime import datetime
import os, random, httpx
from app.utils.supabase_auth import supabase, USERS_TABLE
from app.models.user_model import VocabCard

EXTERNAL_WORD_API = os.getenv("EXTERNAL_WORD_API")
EXTERNAL_WORD_API_KEY = os.getenv("EXTERNAL_WORD_API_KEY")
DEFAULT_PRACTICE_BATCH = int(os.getenv("DEFAULT_PRACTICE_BATCH", "10"))

FALLBACK_WORDS = [
    {"word": "aberration", "meaning": "a deviation from the norm", "example": "A temporary aberration in behavior."},
    {"word": "belie", "meaning": "to give a false impression", "example": "The short statement belied the complexity."},
    {"word": "capitulate", "meaning": "to surrender", "example": "They will not capitulate to pressure."},
    {"word": "deleterious", "meaning": "harmful", "example": "Smoking has deleterious effects."},
    {"word": "ebullient", "meaning": "cheerful and full of energy", "example": "She was ebullient after the win."}
]


async def fetch_words_from_external_api(count: int = 20, proficiency: str = "beginner") -> List[Dict[str, str]]:
    if not EXTERNAL_WORD_API:
        return random.sample(FALLBACK_WORDS, min(count, len(FALLBACK_WORDS)))
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(EXTERNAL_WORD_API, params={"limit": count, "proficiency": proficiency})
            r.raise_for_status()
            data = r.json()
            words = [{"word": w.get("word", w), "meaning": w.get("definition", None), "example": w.get("example", None)} for w in data]
            return words[:count]
    except Exception:
        return random.sample(FALLBACK_WORDS, min(count, len(FALLBACK_WORDS)))


def get_user_row(user_email: str) -> Optional[Dict[str, Any]]:
    resp = supabase.table(USERS_TABLE).select("*").eq("email", user_email).limit(1).execute()
    if not resp.data:
        raise RuntimeError("User not found")
    return resp.data[0]


def update_user_row(user_email: str, patch: Dict[str, Any]):
    resp = supabase.table(USERS_TABLE).update(patch).eq("email", user_email).execute()
    if resp.error:
        raise RuntimeError(f"Supabase error: {resp.error}")
    return resp.data


def list_vocab_cards(user_email: str) -> List[VocabCard]:
    user = get_user_row(user_email)
    cards = user.get("vocab_cards") or []
    return [VocabCard(**c) for c in cards]


def add_vocab_card(user_email: str, card: VocabCard) -> Dict:
    user = get_user_row(user_email)
    cards = user.get("vocab_cards") or []
    if any(c.get("word").lower() == card.word.lower() for c in cards):
        raise ValueError("Word already exists in your vocab cards.")
    cards.append(card.model_dump())
    update_user_row(user_email, {"vocab_cards": cards})
    return card.model_dump()


def update_vocab_card(user_email: str, word: str, patch: Dict) -> Dict:
    user = get_user_row(user_email)
    cards = user.get("vocab_cards") or []
    for c in cards:
        if c.get("word").lower() == word.lower():
            c.update(patch)
            break
    update_user_row(user_email, {"vocab_cards": cards})
    return patch


def delete_vocab_card(user_email: str, word: str):
    user = get_user_row(user_email)
    cards = [c for c in user.get("vocab_cards", []) if c.get("word").lower() != word.lower()]
    update_user_row(user_email, {"vocab_cards": cards})


def get_practice_batch(user_email: str, batch_size: int = DEFAULT_PRACTICE_BATCH) -> List[Dict]:
    cards = list_vocab_cards(user_email)
    cards_sorted = sorted(cards, key=lambda c: (c.level, c.added_at))
    selected = random.sample(cards_sorted, min(batch_size, len(cards_sorted)))
    return [c.model_dump() for c in selected]


def process_practice_result(user_email: str, word: str, correct: bool, time_ms: Optional[int] = None) -> Dict:
    user = get_user_row(user_email)
    cards = user.get("vocab_cards") or []
    gam = user.get("gamification") or {"points": 0, "streak": 0}

    for c in cards:
        if c.get("word").lower() == word.lower():
            if correct:
                c["level"] = min(10, c.get("level", 1) + 1)
                gam["points"] += 5
                gam["streak"] += 1
            else:
                c["level"] = max(1, c.get("level", 1) - 1)
                gam["streak"] = 0
            c.setdefault("practice_history", []).append({
                "ts": datetime.utcnow().isoformat(),
                "correct": correct,
                "time_ms": time_ms
            })
            break

    update_user_row(user_email, {"vocab_cards": cards, "gamification": gam})
    return {"updated_word": word, "gamification": gam}
