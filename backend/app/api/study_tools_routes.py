from flask import Blueprint, request, jsonify
from app.utils.auth_decorator import token_required
from app.services.study_service import study_service

study_tools_routes = Blueprint('study_tools_routes', __name__)

@study_tools_routes.route('/vocabulary', methods=['POST'])
@token_required
def add_word(current_user):
    """
    Adds a new word to the user's vocabulary list.
    """
    data = request.get_json()
    if not data or not data.get('word') or not data.get('definition'):
        return jsonify({'message': 'Word and definition are required'}), 400

    try:
        word_id = study_service.add_vocabulary_word(current_user['id'], data)
        return jsonify({'message': 'Word added successfully', 'id': str(word_id)}), 201
    except Exception as e:
        return jsonify({'message': f'An error occurred: {e}'}), 500


@study_tools_routes.route('/mains-answer', methods=['POST'])
@token_required
def generate_answer(current_user):
    """
    Generates a UPSC Mains style answer from a collection of articles.
    """
    data = request.get_json()
    article_ids = data.get('article_ids')

    if not article_ids or not isinstance(article_ids, list):
        return jsonify({'message': 'A list of article_ids is required'}), 400

    try:
        answer = study_service.generate_mains_answer(article_ids)
        return jsonify({'generated_answer': answer}), 200
    except Exception as e:
        return jsonify({'message': f'An error occurred: {e}'}), 500

