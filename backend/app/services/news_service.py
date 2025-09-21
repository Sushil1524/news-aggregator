from app.core.db import mongo
from bson.objectid import ObjectId
import datetime

class NewsService:
    def get_paginated_feed(self, page=1, per_page=10):
        """
        Fetches a paginated list of articles from the database, sorted by date.
        """
        skip = (page - 1) * per_page
        # Sort by most recent first
        articles_cursor = mongo.db.articles.find().sort('published_at', -1).skip(skip).limit(per_page)
        
        articles = []
        for article in articles_cursor:
            article['_id'] = str(article['_id']) # Convert ObjectId to string for JSON serialization
            articles.append(article)
            
        return articles

    def find_article_by_id(self, article_id):
        """
        Finds a single article by its ID.
        """
        try:
            object_id = ObjectId(article_id)
        except Exception:
            return None # Invalid ID format
        
        article = mongo.db.articles.find_one({'_id': object_id})
        if article:
            article['_id'] = str(article['_id'])
        return article

    def vote_on_article(self, article_id, vote_type):
        """
        Increments or decrements the vote count for an article.
        """
        increment = 1 if vote_type == 'upvote' else -1
        result = mongo.db.articles.update_one(
            {'_id': ObjectId(article_id)},
            {'$inc': {'votes': increment}}
        )
        return result.modified_count > 0

    def add_comment_to_article(self, article_id, user_id, username, text):
        """
        Adds a new comment to an article's comment list.
        """
        comment = {
            '_id': ObjectId(), # Generate a new ID for the comment
            'user_id': ObjectId(user_id),
            'username': username,
            'text': text,
            'created_at': datetime.datetime.now(datetime.timezone.utc)
        }
        
        result = mongo.db.articles.update_one(
            {'_id': ObjectId(article_id)},
            {'$push': {'comments': comment}}
        )
        return result.modified_count > 0

# Instantiate the service
news_service = NewsService()
