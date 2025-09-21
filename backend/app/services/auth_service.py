import bcrypt
import jwt
import datetime
from flask import current_app
from app.core.db import mongo
from app.models.user_model import validate_user_data
from bson.objectid import ObjectId

class AuthService:
    def register_user(self, data):
        """
        Handles the logic for registering a new user.
        - Validates data
        - Checks for existing user
        - Hashes password
        - Inserts into DB
        """
        try:
            validate_user_data(data)
        except ValueError as e:
            raise ValueError(f"Invalid user data: {e}")

        # Check if user already exists
        if mongo.db.users.find_one({'email': data['email']}):
            raise ValueError("A user with this email already exists.")

        # Hash the password for security
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Prepare user document for insertion
        user_doc = {
            "email": data['email'],
            "username": data['username'],
            "password": hashed_password,
            "created_at": datetime.datetime.now(datetime.timezone.utc),
            "gamification": {
                'points': 0,
                'streak': 0,
                'last_active_date': None
            }
        }
        
        # Insert user and return their new ID
        result = mongo.db.users.insert_one(user_doc)
        return result.inserted_id

    def login_user(self, email, password):
        """
        Handles user login.
        - Finds user by email
        - Verifies password
        - Generates a JWT token
        """
        user = mongo.db.users.find_one({'email': email})

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Password is correct, generate JWT token
            token = jwt.encode({
                'user_id': str(user['_id']),
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
            }, current_app.config['SECRET_KEY'], algorithm="HS256")
            
            return token
        
        # If user not found or password incorrect
        return None

# Instantiate the service so it can be imported and used easily
auth_service = AuthService()
