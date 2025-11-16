"""Flask application factory for Lakehead University Chatbot backend."""
import logging
import os

from flask import Flask
from flask_cors import CORS


def create_app(config_object=None):
    """Create and configure Flask application.

    Args:
        config_object: Optional configuration object or dictionary

    Returns:
        Flask: Configured Flask application instance
    """

    backend_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    project_root = os.path.dirname(backend_root)

    frontend_dir  = os.path.join(project_root, "frontend")
    templates_dir = os.path.join(frontend_dir, "templates")
    static_dir    = os.path.join(frontend_dir, "static")

    app = Flask(__name__, instance_relative_config=True, template_folder=templates_dir, static_folder=static_dir)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Load default configuration from the app package (app/config.py)
    try:
        app.config.from_object("app.config")
    except (ImportError, AttributeError) as config_error:
        logging.getLogger(__name__).warning(
            "Could not load app.config: %s; using defaults and provided overrides.",
            config_error
        )

    if config_object:
        if isinstance(config_object, dict):
            app.config.update(config_object)
        else:
            app.config.from_object(config_object)

    # Configure CORS for frontend integration
    cors_origins = [
        "http://localhost:3000",  # React development server
        "http://localhost:8080",  # Vue development server
        "https://*.pythonanywhere.com",  # PythonAnywhere domains
        "https://lakehead-chatbot.pythonanywhere.com"  # Production domain
    ]
    CORS(app, origins=cors_origins)

    # Register API with automatic documentation
    from .api_routes import api  # pylint: disable=import-outside-toplevel
    api.init_app(app)

    # Add error handlers
    @app.errorhandler(404)
    def not_found(_error):
        """Handle 404 errors."""
        return {"error": "Endpoint not found"}, 404

    @app.errorhandler(405)
    def method_not_allowed(_error):
        """Handle 405 errors."""
        return {"error": "Method not allowed"}, 405

    @app.errorhandler(500)
    def internal_error(_error):
        """Handle 500 errors."""
        logging.error("Internal server error occurred")
        return {"error": "Internal server error"}, 500

    return app
