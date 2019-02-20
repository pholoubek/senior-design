from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config



def register_app_blueprints(app):
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    return app
    
#  keep at the bottom to prevent circular imports
#  from app import routes

