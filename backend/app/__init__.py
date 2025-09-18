from flask import Flask
import logging

def create_app(config_object: object = None) -> Flask:

    app = Flask(__name__, instance_relative_config=True)

    # Load default configuration from the app package (app/config.py)
    try:
        app.config.from_object("app.config")
    except Exception:
        logging.getLogger(__name__).warning("Could not load app.config; using defaults and provided overrides.")

    if config_object:
        if isinstance(config_object, dict):
            app.config.update(config_object)
        else:
            app.config.from_object(config_object)

    # Register blueprints
    from .routes import bp as routes_bp

    app.register_blueprint(routes_bp)

    return app
