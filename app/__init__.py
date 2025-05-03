from flask import Flask
from app.extensions import db, login_manager, csrf, api_ref
from config import Config
from datetime import datetime


def format_date(value, format='%b %d, %Y'):
    """Format a date safely."""
    if value is None:
        return "N/A"
    
    if isinstance(value, datetime):
        return value.strftime(format)
    
    if isinstance(value, str):
        # Try to parse the string to a date
        try:
            # Handle ISO format with T
            if 'T' in value:
                value = value.replace('T', ' ')
            
            # Try different date formats
            if ' ' in value:  # Has time component
                try:
                    # Try datetime format first
                    parsed_date = datetime.strptime(value.split('.')[0], '%Y-%m-%d %H:%M:%S')
                    return parsed_date.strftime(format)
                except ValueError:
                    # Fall back to just date parsing
                    parsed_date = datetime.strptime(value.split(' ')[0], '%Y-%m-%d')
                    return parsed_date.strftime(format)
            else:  # Just date
                parsed_date = datetime.strptime(value, '%Y-%m-%d')
                return parsed_date.strftime(format)
        except ValueError as e:
            try:
                # Try just parsing the first 10 chars (YYYY-MM-DD)
                if len(value) >= 10:
                    parsed_date = datetime.strptime(value[:10], '%Y-%m-%d')
                    return parsed_date.strftime(format)
            except (ValueError, TypeError):
                pass
            return value
    
    return str(value)


def to_datetime(value, format='%Y-%m-%d'):
    """Convert a string to datetime."""
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return value
    
    try:
        return datetime.strptime(value, format)
    except (ValueError, TypeError):
        return None


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Register custom template filters
    app.jinja_env.filters['format_date'] = format_date
    app.jinja_env.filters['to_datetime'] = to_datetime

    # Register blueprints
    from .views import auth, sponsor, influencer, admin, main

    app.register_blueprint(auth.auth)
    app.register_blueprint(sponsor.sponsor, url_prefix="/sponsor")
    app.register_blueprint(influencer.influencer, url_prefix="/influencer")
    app.register_blueprint(main.main)
    app.register_blueprint(admin.admin)

    with app.app_context():
        db.create_all()

    return app

