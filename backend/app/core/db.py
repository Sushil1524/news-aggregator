from flask import current_app
from flask_pymongo import PyMongo

# Initialize a PyMongo object. This will be configured with the app in the factory.
mongo = PyMongo()

def init_db(app):
    """
    Initializes the database connection with the Flask app.
    This function is called from the application factory.
    """
    mongo.init_app(app)
    current_app.logger.info("MongoDB connection initialized.")