from datetime import date, datetime, timedelta
from app.utils.supabase_auth import supabase
import random, json, os

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


def refresh_daily_vocab():
    """Runs once daily: refresh vocab sets and handle streaks."""
    today = date.today()
    print(f"[Vocab Scheduler] Running daily refresh for {today}...")

    # Fetch all users with vocab-related fields
    users = supabase.table("users").select(
        "id, vocab_cards, daily_practice_target, vocab_proficiency, gamification"
    ).execute()

    if not users.data:
        print("[Vocab Scheduler] No users found.")
        return

    for user in users.data:
        vocab_cards = user.get("vocab_cards") or []
        gamification = user.get("gamification") or {"points": 0, "streak": 0}
        daily_target = user.get("daily_practice_target") or 10
        proficiency = user.get("vocab_proficiency") or "beginner"

        # Ensure gamification fields always exist
        gamification.setdefault("points", 0)
        gamification.setdefault("streak", 0)

        # --- 1️⃣ Streak maintenance ---
        last_practice_dates = [
            date.fromisoformat(c["last_practiced"])
            for c in vocab_cards
            if c.get("last_practiced")
        ]

        if last_practice_dates:
            last_day = max(last_practice_dates)
            day_gap = (today - last_day).days
            if day_gap > 1:
                # Missed more than a day → reset streak
                gamification["streak"] = 0
            elif day_gap == 1:
                # Practiced yesterday → maintain streak
                gamification["streak"] += 1
            # if day_gap == 0 → already practiced today (no change)
        else:
            # No practice yet → start from 0
            gamification["streak"] = 0

        # --- 2️⃣ New vocab preparation ---
        due_today = [
            c for c in vocab_cards
            if c.get("next_review_date")
            and date.fromisoformat(c["next_review_date"]) <= today
        ]

        if len(due_today) < daily_target:
            needed = daily_target - len(due_today)
            existing_words = {c["word"] for c in vocab_cards}
            available_words = [w for w in ALL_WORDS if w not in existing_words]

            # Only sample if enough new words exist
            if available_words:
                new_words = random.sample(available_words, min(needed, len(available_words)))

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

        # --- 3️⃣ Push updates to Supabase ---
        try:
            supabase.table("users").update({
                "vocab_cards": vocab_cards,
                "gamification": gamification
            }).eq("id", user["id"]).execute()
        except Exception as e:
            print(f"[Vocab Scheduler] ❌ Failed to update user {user['id']}: {e}")

    print("[Vocab Scheduler] ✅ Daily vocab refresh complete!")