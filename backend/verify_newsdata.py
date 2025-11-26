import asyncio
import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.news_pipeline import fetch_and_process_newsdata

NEWSDATA_API_KEY = "pub_156fd4301a2c41df9370ecf723118f43"

async def main():
    print("🚀 Starting NewsData.io verification...")
    try:
        await fetch_and_process_newsdata(NEWSDATA_API_KEY)
        print("✅ Verification completed successfully.")
    except Exception as e:
        print(f"❌ Verification failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
