# import os
# from flask import Flask, jsonify
# from config import config
# from .core.db import mongo
# from flask_cors import CORS

# def create_app(config_name=None):
#     """
#     Application factory function.
#     Initializes the Flask application, configures it, and registers blueprints.
#     """
#     if config_name is None:
#         config_name = os.getenv('FLASK_CONFIG', 'default')

#     app = Flask(__name__)
#     app.config.from_object(config[config_name])
#     config[config_name].init_app(app)

#     # --- Initialize Extensions ---
#     # Initialize CORS to allow cross-origin requests from the frontend
#     CORS(app)
    
#     # Initialize MongoDB with the app context
#     mongo.init_app(app)

#     # --- Register Blueprints ---
#     # Import and register the main API blueprint
#     from .api import api_bp
#     app.register_blueprint(api_bp, url_prefix='/api')

#     # --- Global Error Handlers ---
#     @app.errorhandler(500)
#     def internal_server_error(e):
#         """
#         Global handler for internal server errors.
#         Ensures a JSON response is sent for unexpected errors.
#         """
#         app.logger.error(f"Internal Server Error: {e}")
#         return jsonify(message="An unexpected internal server error occurred."), 500
        
#     @app.errorhandler(404)
#     def page_not_found(e):
#         """
#         Global handler for 404 Not Found errors.
#         """
#         return jsonify(message="The requested resource was not found."), 404

#     return app

# app/__init__.py

import os
from dotenv import load_dotenv

# Load environment variables automatically when app package is imported
load_dotenv()

# Optional: ensure key directories exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
MODELS_DIR = os.path.join(BASE_DIR, "models")
ROUTES_DIR = os.path.join(BASE_DIR, "routes")
SERVICES_DIR = os.path.join(BASE_DIR, "services")
UTILS_DIR = os.path.join(BASE_DIR, "utils")

__all__ = ["CONFIG_DIR", "MODELS_DIR", "ROUTES_DIR", "SERVICES_DIR", "UTILS_DIR"]
