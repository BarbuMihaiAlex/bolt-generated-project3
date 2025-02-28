"""
This module initializes and sets up the containers plugin for CTFd.
"""

from flask import Flask
from flask.blueprints import Blueprint
import sqlite3
from sqlalchemy import inspect

from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.models import db

from .container_challenge import ContainerChallenge
from .setup import setup_default_configs
from .routes import register_app
from .logs import init_logs

def create_tables(app: Flask):
    """
    Safely create or update database tables.
    """
    with app.app_context():
        inspector = inspect(db.engine)
        
        # Check if tables exist and create/modify as needed
        if not inspector.has_table("container_challenge_model"):
            # Create ContainerChallengeModel table
            db.Model.metadata.tables["container_challenge_model"].create(db.engine)
        else:
            # Add new columns if they don't exist
            columns = [c["name"] for c in inspector.get_columns("container_challenge_model")]
            with db.engine.connect() as conn:
                if "port_range_start" not in columns:
                    conn.execute('ALTER TABLE container_challenge_model ADD COLUMN port_range_start INTEGER')
                if "port_range_end" not in columns:
                    conn.execute('ALTER TABLE container_challenge_model ADD COLUMN port_range_end INTEGER')

        if not inspector.has_table("container_info_model"):
            # Create ContainerInfoModel table
            db.Model.metadata.tables["container_info_model"].create(db.engine)
        else:
            # Add new columns if they don't exist
            columns = [c["name"] for c in inspector.get_columns("container_info_model")]
            with db.engine.connect() as conn:
                if "ports" not in columns:
                    conn.execute('ALTER TABLE container_info_model ADD COLUMN ports TEXT')

        if not inspector.has_table("container_settings_model"):
            # Create ContainerSettingsModel table
            db.Model.metadata.tables["container_settings_model"].create(db.engine)

def load(app: Flask) -> None:
    """
    Initialize and set up the containers plugin for CTFd.
    """
    app.config['RESTX_ERROR_404_HELP'] = False

    try:
        # Safely create/update database tables
        create_tables(app)
        
        # Initialize default settings
        setup_default_configs()
        
        # Register the challenge type
        CHALLENGE_CLASSES["container"] = ContainerChallenge
        
        # Register plugin assets
        register_plugin_assets_directory(app, base_path="/plugins/containers/assets/")

        # Initialize logging
        init_logs(app)

        # Register blueprint
        containers_bp: Blueprint = register_app(app)
        app.register_blueprint(containers_bp)
        
    except Exception as e:
        print(f"Error initializing containers plugin: {str(e)}")
        # Continue loading CTFd even if plugin fails
        pass
