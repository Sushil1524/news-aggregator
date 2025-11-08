from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta, date
from app.utils.supabase_auth import supabase
from app.models.user_model import VocabProficiency
from app.utils.dependencies import get_current_user
import random, json, os

router = APIRouter()

WORDS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
    "app",
    "data", 
    "words_dictionary.json"
)

def load_words():
    try:
        with open(WORDS_PATH, "r", encoding="utf-8") as f:
            return list(json.load(f).keys())
    except FileNotFoundError:
        print(f"Error: Could not find dictionary file at {WORDS_PATH}")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in dictionary file at {WORDS_PATH}")
        return []


ALL_WORDS = load_words()


@router.get("/today")
async def get_daily_vocab(user=Depends(get_current_user)):
    """Return today's vocab cards for the user based on proficiency & target."""
    user_data = (
        supabase.table("users")
        .select("id, vocab_cards, daily_practice_target, vocab_proficiency")
        .eq("id", user["id"])
        .single()
        .execute()
    )

    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")

    user_entry = user_data.data
    vocab_cards = user_entry.get("vocab_cards", []) or []
    daily_target = user_entry.get("daily_practice_target", 10)
    proficiency = user_entry.get("vocab_proficiency", VocabProficiency.BEGINNER.value)
    today = date.today()

    # Filter cards due for review today
    due_cards = [
        c for c in vocab_cards
        if c.get("next_review_date")
        and date.fromisoformat(c["next_review_date"]) <= today
    ]
    available = due_cards[:daily_target]

    # Add new words if fewer than daily goal
    if len(available) < daily_target:
        needed = daily_target - len(available)
        existing_words = {c["word"] for c in vocab_cards}
        new_words = random.sample(
            [w for w in ALL_WORDS if w not in existing_words], needed
        )

        for w in new_words:
            vocab_cards.append({
                "word": w,
                "meaning": None,
                "example": None,
                "added_at": datetime.utcnow().isoformat(),
                "level": 1,
                "proficiency": proficiency,
                "next_review_date": today.isoformat(),
                "last_practiced": None,
                "is_learned": False
            })

        available.extend([c for c in vocab_cards if c["word"] in new_words])

        # Save back updated vocab_cards
        supabase.table("users").update({"vocab_cards": vocab_cards}).eq("id", user["id"]).execute()

    return {"today_cards": available, "daily_target": daily_target}


@router.post("/practice/done")
async def mark_practice_done(payload: dict, user=Depends(get_current_user)):
    """Mark practiced vocab cards and update levels inside users.vocab_cards JSONB."""
    practiced_words = payload.get("words", [])
    if not practiced_words:
        raise HTTPException(status_code=400, detail="No practiced words provided")

    user_data = (
        supabase.table("users")
        .select("vocab_cards, gamification")
        .eq("id", user["id"])
        .single()
        .execute()
    )

    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")

    vocab_cards = user_data.data.get("vocab_cards", []) or []
    gamification = user_data.data.get("gamification", {"points": 0, "streak": 0})
    today = date.today()
    practiced_today = 0

    for card in vocab_cards:
        if card["word"] in practiced_words:
            card["level"] = card.get("level", 1) + 1
            card["last_practiced"] = today.isoformat()
            card["next_review_date"] = (today + timedelta(days=card["level"] * 2)).isoformat()
            card["is_learned"] = card["level"] >= 5
            practiced_today += 1

    # Simple gamification logic
    gamification["points"] += practiced_today * 10  # 10 pts per word
    gamification["streak"] += 1  # increment streak (later can reset if missed day)

    # Save updated vocab & gamification
    supabase.table("users").update({
        "vocab_cards": vocab_cards,
        "gamification": gamification
    }).eq("id", user["id"]).execute()

    return {"message": "Practice progress updated successfully"}


@router.get("/progress")
async def get_vocab_progress(user=Depends(get_current_user)):
    """Return vocab learning progress summary for gamification and analytics."""
    user_data = (
        supabase.table("users")
        .select("vocab_cards, gamification, daily_practice_target")
        .eq("id", user["id"])
        .single()
        .execute()
    )

    if not user_data.data:
        raise HTTPException(status_code=404, detail="User not found")

    vocab_cards = user_data.data.get("vocab_cards", []) or []
    gamification = user_data.data.get("gamification", {"points": 0, "streak": 0})
    daily_target = user_data.data.get("daily_practice_target", 10)
    today = date.today()

    total_learned = sum(1 for c in vocab_cards if c.get("is_learned"))
    due_today = sum(
        1
        for c in vocab_cards
        if c.get("next_review_date")
        and date.fromisoformat(c["next_review_date"]) <= today
    )
    practiced_today = sum(
        1
        for c in vocab_cards
        if c.get("last_practiced") and date.fromisoformat(c["last_practiced"]) == today
    )

    completion_rate = round((practiced_today / daily_target) * 100, 2) if daily_target else 0

    return {
        "summary": {
            "total_words": len(vocab_cards),
            "total_learned": total_learned,
            "due_today": due_today,
            "practiced_today": practiced_today,
            "daily_target": daily_target,
            "completion_rate": completion_rate,
        },
        "gamification": gamification,
    }
