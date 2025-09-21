import datetime

def get_analytics_schema():
    """
    Returns the schema for a user's analytics document.
    Each user will have one such document.
    """
    return {
        'user_id': {'type': 'objectid', 'required': True, 'unique': True},
        'articles_read_ids': {'type': 'list', 'schema': {'type': 'objectid'}},
        'daily_reading_history': {
            'type': 'list',
            'schema': {
                'type': 'dict',
                'schema': {
                    'date': {'type': 'date'},
                    'count': {'type': 'integer'}
                }
            }
        },
        'vocab_added_count': {'type': 'integer', 'default': 0},
        'last_updated': {'type': 'datetime', 'default': datetime.datetime.now(datetime.timezone.utc)}
    }
