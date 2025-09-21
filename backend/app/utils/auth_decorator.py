import jwt
from functools import wraps
from flask import request, jsonify, current_app
from app.core.db import mongo
from bson.objectid import ObjectId
from bson.errors import InvalidId

def token_required(f):
    """
    A decorator to ensure a valid JWT token is present in the request header
    and to pass the authenticated user to the decorated function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Check if 'Authorization' header is present
        if 'Authorization' in request.headers:
            # The header should be in the format 'Bearer <token>'
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Malformed Authorization header. Use "Bearer <token>".'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            # Decode the token using the app's secret key
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # --- Real User Lookup from Database ---
            # Find the user in the database using the ID from the token.
            # Note: This requires the JWT's 'user_id' to be the string representation
            # of the user's MongoDB '_id'.
            try:
                user_id = ObjectId(data['user_id'])
                current_user_from_db = mongo.db.users.find_one({'_id': user_id})
            except (InvalidId, TypeError):
                 return jsonify({'message': 'Invalid user ID format in token.'}), 401

            if not current_user_from_db:
               return jsonify({'message': 'User not found!'}), 401
            
            # Create a user object to pass to the route, excluding sensitive info like password.
            current_user = {
                'id': str(current_user_from_db['_id']),
                'email': current_user_from_db.get('email'),
                'username': current_user_from_db.get('username')
            }
            # --- END ---

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            current_app.logger.error(f"Error decoding token: {e}")
            return jsonify({'message': 'An error occurred while processing the token.'}), 500
        
        # Pass the authenticated user object to the decorated route
        return f(current_user, *args, **kwargs)

    return decorated

