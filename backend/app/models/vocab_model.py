import datetime

def get_vocab_schema():
    """
    Returns the schema for a vocabulary entry document.
    """
    return {
        'user_id': {'type': 'objectid', 'required': True},
        'word': {'type': 'string', 'required': True},
        'definition': {'type': 'string', 'required': True},
        'example_sentence': {'type': 'string', 'nullable': True},
        'added_at': {'type': 'datetime', 'default': datetime.datetime.now(datetime.timezone.utc)},
        'srs_data': { # Spaced Repetition System data
            'type': 'dict',
            'schema': {
                'due_date': {'type': 'date', 'required': True},
                'interval_days': {'type': 'integer', 'default': 1},
                'ease_factor': {'type': 'float', 'default': 2.5}
            }
        }
    }
