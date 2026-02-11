from flask import Flask
from flask_session import Session
from app.config import Config
from app.services import llm_service


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    Session(app)

    # Initialize Gemini
    llm_service.configure(app.config["GEMINI_API_KEY"])

    # Register routes
    from app.routes import main
    app.register_blueprint(main)

    return app