"""
WSGI entry point for production deployment.
Used by gunicorn and other WSGI servers.
"""

import os
from app import create_app

# Set environment for production if not specified
if not os.environ.get('FLASK_ENV'):
    os.environ['FLASK_ENV'] = 'production'

# Create application instance
application = create_app()

if __name__ == "__main__":
    application.run()