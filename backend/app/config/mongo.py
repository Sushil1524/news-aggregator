# app/config/mongo.py

from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection string from .env
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "news_aggregator")

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Collections (for type hinting and easy imports)
raw_articles_collection = db["raw_articles"]
articles_collection = db["articles"]
comments_collection = db["comments"]
analytics_collection = db["analytics"]
pipeline_logs_collection = db["pipeline_logs"]
feeds_metadata_collection = db["feeds_metadata"]

print(f"✅ Connected to MongoDB database: {MONGO_DB_NAME}")
