# app/__init__.py
from flask import Flask
from flask_cors import CORS
from config import Config
from app.database import db, ma
import logging
from logging.handlers import RotatingFileHandler
import os

def create_app(config_class=Config):
    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize CORS
    CORS(app, resources={
        r"*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)

    from app.routes import (
        courses_bp, programs_bp, offerings_bp,
        blocks_bp, requirements_bp, schedules_bp, conflicts_bp
    )
    
    app.register_blueprint(courses_bp)
    app.register_blueprint(programs_bp)
    app.register_blueprint(offerings_bp)
    app.register_blueprint(blocks_bp)
    app.register_blueprint(requirements_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(conflicts_bp)

    return app