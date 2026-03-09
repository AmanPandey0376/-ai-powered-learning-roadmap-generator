"""
Main Flask application entry point and configuration.
Initializes the Flask app, configures CORS, and registers blueprints.
"""

import os
import logging
from flask import Flask, render_template_string
from flask_cors import CORS
from dotenv import load_dotenv
from utils.helpers import setup_logging
from config import get_config

# Load environment variables from .env file
load_dotenv()

def create_app():
    """Application factory pattern for creating Flask app."""
    # Get configuration based on environment
    config_class = get_config()
    
    # Initialize logging
    setup_logging(config_class.LOG_LEVEL)
    
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    
    # Configure CORS for frontend integration
    CORS(app, origins=config_class.CORS_ORIGINS)
    
    logging.info(f"Flask application initialized with {config_class.__name__}")
    
    # Register blueprints
    from routes.roadmap_routes import roadmap_bp
    from routes.resources_routes import resources_bp
    from routes.realtime_roadmap import realtime_roadmap_bp
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(resources_bp)
    app.register_blueprint(realtime_roadmap_bp)
    
    @app.route('/')
    def root():
        """Root endpoint - API information page."""
        # Check if request wants JSON (API client) or HTML (browser)
        from flask import request
        
        if request.headers.get('Accept', '').find('application/json') != -1:
            # Return JSON for API clients
            return {
                'message': 'Learning Roadmap Generator API',
                'version': '1.0.0',
                'status': 'running',
                'endpoints': {
                    'health': {
                        'url': '/health',
                        'method': 'GET',
                        'description': 'Health check endpoint'
                    },
                    'roadmap': {
                        'url': '/api/roadmap',
                        'method': 'POST',
                        'description': 'Generate learning roadmap for a skill',
                        'example': {
                            'request': {'skill': 'react developer'},
                            'response': 'Roadmap with modules and projects'
                        }
                    },
                    'resources': {
                        'url': '/api/resources/<skill>',
                        'method': 'GET',
                        'description': 'Get learning resources for a skill',
                        'example': {
                            'request': '/api/resources/react%20developer',
                            'response': 'Free and paid learning resources'
                        }
                    }
                },
                'frontend': {
                    'url': 'http://localhost:3000',
                    'description': 'React frontend application'
                },
                'documentation': {
                    'roadmap_info': '/api/roadmap (GET)',
                    'resources_info': '/api/resources (GET)'
                }
            }
        else:
            # Return HTML for browsers
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Learning Roadmap Generator API</title>
                <style>
                    body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
                    .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #2563eb; margin-bottom: 10px; }
                    .status { color: #059669; font-weight: bold; }
                    .endpoint { background: #f8fafc; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #2563eb; }
                    .method { background: #2563eb; color: white; padding: 2px 8px; border-radius: 3px; font-size: 12px; }
                    .frontend-link { background: #059669; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }
                    .frontend-link:hover { background: #047857; }
                    code { background: #e5e7eb; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 Learning Roadmap Generator API</h1>
                    <p>Status: <span class="status">✅ Running</span></p>
                    <p>Version: 1.0.0</p>
                    
                    <h2>📱 Frontend Application</h2>
                    <p>The React frontend is available at:</p>
                    <a href="http://localhost:3000" class="frontend-link" target="_blank">
                        Open Frontend Application →
                    </a>
                    
                    <h2>🔌 API Endpoints</h2>
                    
                    <div class="endpoint">
                        <h3><span class="method">GET</span> /health</h3>
                        <p>Health check endpoint to verify the API is running.</p>
                        <p><strong>Example:</strong> <code>GET http://localhost:5001/health</code></p>
                    </div>
                    
                    <div class="endpoint">
                        <h3><span class="method">POST</span> /api/roadmap</h3>
                        <p>Generate a learning roadmap for a specific skill.</p>
                        <p><strong>Request Body:</strong> <code>{"skill": "react developer"}</code></p>
                        <p><strong>Example:</strong> <code>POST http://localhost:5001/api/roadmap</code></p>
                    </div>
                    
                    <div class="endpoint">
                        <h3><span class="method">GET</span> /api/resources/&lt;skill&gt;</h3>
                        <p>Get learning resources for a specific skill.</p>
                        <p><strong>Example:</strong> <code>GET http://localhost:5001/api/resources/react%20developer</code></p>
                    </div>
                    
                    <h2>📚 Documentation</h2>
                    <p>For detailed API documentation:</p>
                    <ul>
                        <li><a href="/api/roadmap">GET /api/roadmap</a> - Roadmap endpoint info</li>
                        <li><a href="/api/resources">GET /api/resources</a> - Resources endpoint info</li>
                    </ul>
                    
                    <h2>🛠️ Integration Status</h2>
                    <p>✅ Backend API is running and ready</p>
                    <p>✅ CORS configured for frontend integration</p>
                    <p>✅ All endpoints tested and functional</p>
                    
                    <hr style="margin: 30px 0;">
                    <p style="text-align: center; color: #6b7280;">
                        Learning Roadmap Generator Backend API v1.0.0
                    </p>
                </div>
            </body>
            </html>
            """
            return render_template_string(html_template)
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        logging.info("Health check endpoint accessed")
        return {'status': 'healthy', 'message': 'Flask backend is running'}
    
    logging.info("Flask application configuration complete")
    return app

if __name__ == '__main__':
    app = create_app()
    config_class = get_config()
    logging.info(f"Starting Flask server on {config_class.HOST}:{config_class.PORT}")
    app.run(debug=config_class.DEBUG, host=config_class.HOST, port=config_class.PORT)