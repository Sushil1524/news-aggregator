import os
from app import create_app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the configuration name from the environment or use 'default'
config_name = os.getenv('FLASK_ENV', 'development')

# Create the Flask application instance using the factory function
app = create_app(config_name)

if __name__ == '__main__':
    # Run the application
    # The host and port can also be configured in the .env file
    # For development, Flask's built-in server is sufficient.
    # For production, a WSGI server like Gunicorn should be used.
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))