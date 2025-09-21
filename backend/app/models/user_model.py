import datetime

def get_user_schema():
    """
    Returns the basic schema structure for a user document.
    This is for validation and ensuring consistency.
    """
    return {
        'email': {'type': 'string', 'required': True, 'unique': True},
        'username': {'type': 'string', 'required': True},
        'password': {'type': 'string', 'required': True}, # Stored as a hash
        'created_at': {'type': 'datetime', 'default': datetime.datetime.now(datetime.timezone.utc)},
        'gamification': {
            'type': 'dict',
            'schema': {
                'points': {'type': 'integer', 'default': 0},
                'streak': {'type': 'integer', 'default': 0},
                'last_active_date': {'type': 'date', 'nullable': True}
            }
        }
    }

def validate_user_data(data):
    """
    A simple validator for user data before insertion.
    In a real app, you might use a more robust library like Cerberus or Marshmallow.
    """
    if not all(k in data for k in ['email', 'username', 'password']):
        raise ValueError("Email, username, and password are required.")
    if not isinstance(data.get('email'), str) or '@' not in data.get('email'):
        raise ValueError("A valid email is required.")
    return True
