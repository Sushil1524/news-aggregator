import jwt
import datetime
from functools import wraps
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.auth_decorator import token_required

# --- Placeholder Services & Models ---
# In a real app, this logic would live in dedicated service/model files.
class UserService:
    # MOCK: In-memory user store for demonstration
    users = {} 
    
    def find_user_by_email(self, email):
        return self.users.get(email)

    def save_user(self, email, username, hashed_password):
        if email in self.users:
            raise ValueError("User with this email already exists.")
        self.users[email] = {"username": username, "email": email, "password": hashed_password, "id": f"user_{len(self.users)+1}"}
        return self.users[email]

auth_service = UserService()
# --- End Placeholder ---

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    """
    Endpoint for user registration.
    Expects JSON body with 'username', 'email', and 'password'.
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Email and password are required!'}), 400

    email = data['email']
    username = data.get('username', email)
    
    if auth_service.find_user_by_email(email):
        return jsonify({'message': 'User already exists!'}), 409

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    try:
        new_user = auth_service.save_user(email, username, hashed_password)
        return jsonify({"message": "User registered successfully", "user": {"id": new_user['id'], "email": new_user['email']}}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth.route('/login', methods=['POST'])
def login():
    """
    Endpoint for user login.
    Expects JSON body with 'email' and 'password'.
    Returns a JWT token upon successful authentication.
    """
    auth_data = request.get_json()
    if not auth_data or not auth_data.get('email') or not auth_data.get('password'):
        return jsonify({'message': 'Could not verify'}), 401

    user = auth_service.find_user_by_email(auth_data['email'])

    if not user or not check_password_hash(user['password'], auth_data['password']):
        return jsonify({'message': 'Invalid email or password'}), 401

    # Generate the JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'email': user['email'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})

@auth.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """
    A protected route to get the current user's profile.
    Demonstrates the use of the token_required decorator.
    """
    # The current_user is passed by the decorator
    return jsonify({"user": current_user})

