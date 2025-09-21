from flask import Blueprint, request, jsonify
from app.services.news_service import news_service
from app.utils.auth_decorator import token_required

news_routes = Blueprint('news_routes', __name__)

@news_routes.route('/feed', methods=['GET'])
def get_feed():
    """
    Fetches the main news feed with pagination.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    try:
        articles = news_service.get_paginated_feed(page, per_page)
        return jsonify(articles), 200
    except Exception as e:
        return jsonify({'message': f'An error occurred: {e}'}), 500

@news_routes.route('/articles/<article_id>', methods=['GET'])
def get_article(article_id):
    """
    Fetches a single article by its ID.
    """
    article = news_service.find_article_by_id(article_id)
    if not article:
        return jsonify({'message': 'Article not found'}), 404
    return jsonify(article), 200

@news_routes.route('/articles/<article_id>/vote', methods=['POST'])
@token_required
def vote_article(current_user, article_id):
    """
    Allows a logged-in user to upvote or downvote an article.
    """
    data = request.get_json()
    vote_type = data.get('vote_type') # 'upvote' or 'downvote'
    
    if vote_type not in ['upvote', 'downvote']:
        return jsonify({'message': 'Invalid vote type'}), 400
        
    if not news_service.vote_on_article(article_id, vote_type):
        return jsonify({'message': 'Article not found or could not be updated'}), 404
        
    return jsonify({'message': f'Successfully {vote_type}d article'}), 200

@news_routes.route('/articles/<article_id>/comments', methods=['POST'])
@token_required
def add_comment(current_user, article_id):
    """
    Allows a logged-in user to add a comment to an article.
    Username is securely retrieved from the JWT, not the request body.
    """
    data = request.get_json()
    text = data.get('text')
    
    if not text:
        return jsonify({'message': 'Comment text is required'}), 400
        
    # Get user ID and username from the decorator-provided user object
    user_id = current_user['id']
    username = current_user['username']

    if not news_service.add_comment_to_article(article_id, user_id, username, text):
        return jsonify({'message': 'Article not found or comment could not be added'}), 404
        
    return jsonify({'message': 'Comment added successfully'}), 201

