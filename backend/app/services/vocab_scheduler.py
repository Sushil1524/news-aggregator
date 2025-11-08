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

    # Fetch all users with vocab data
    users = supabase.table("users").select("id, vocab_cards, daily_practice_target, vocab_proficiency, gamification").execute()
    if not users.data:
        print("[Vocab Scheduler] No users found.")
        return

    for user in users.data:
        vocab_cards = user.get("vocab_cards", []) or []
        gamification = user.get("gamification", {"points": 0, "streak": 0})
        daily_target = user.get("daily_practice_target", 10)
        proficiency = user.get("vocab_proficiency", "beginner")

        # 1️⃣ Check streak maintenance
        last_practice_dates = [
            date.fromisoformat(c["last_practiced"])
            for c in vocab_cards
            if c.get("last_practiced")
        ]
        if last_practice_dates:
            last_day = max(last_practice_dates)
            if (today - last_day).days > 1:
                # Missed a day → reset streak
                gamification["streak"] = 0
        else:
            # No practice yet
            gamification["streak"] = 0

        # 2️⃣ Prepare new vocab if user has fewer than daily target due today
        due_today = [
            c for c in vocab_cards
            if c.get("next_review_date")
            and date.fromisoformat(c["next_review_date"]) <= today
        ]

        if len(due_today) < daily_target:
            needed = daily_target - len(due_today)
            existing_words = {c["word"] for c in vocab_cards}
            new_words = random.sample(
                [w for w in ALL_WORDS if w not in existing_words],
                needed
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

        # 3️⃣ Push updates to Supabase
        supabase.table("users").update({
            "vocab_cards": vocab_cards,
            "gamification": gamification
        }).eq("id", user["id"]).execute()

    print("[Vocab Scheduler] ✅ Daily vocab refresh complete!")
