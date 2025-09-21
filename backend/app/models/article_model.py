import datetime
from bson.objectid import ObjectId

def get_article_schema():
    """
    Returns the schema for a synthesized article document.
    """
    return {
        'synthesized_title': {'type': 'string', 'required': True},
        'synthesized_content': {'type': 'string', 'required': True},
        'original_sources': {'type': 'list', 'schema': {'type': 'string'}}, # List of source URLs
        'category': {'type': 'string', 'required': True},
        'published_at': {'type': 'datetime', 'default': datetime.datetime.now(datetime.timezone.utc)},
        'votes': {'type': 'integer', 'default': 0},
        'comments': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    '_id': {'type': 'objectid', 'default': ObjectId()},
                    'user_id': {'type': 'objectid', 'required': True},
                    'username': {'type': 'string', 'required': True},
                    'text': {'type': 'string', 'required': True},
                    'created_at': {'type': 'datetime', 'default': datetime.datetime.now(datetime.timezone.utc)}
                }
            }
        }
    }
