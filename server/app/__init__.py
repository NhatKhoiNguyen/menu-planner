from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from pymongo import MongoClient
import os

load_dotenv()

mongo_client = None
db = None

def create_app():
    global mongo_client, db

    app = Flask(__name__)
    app.config.from_object("config.Config")
    CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL")}}, supports_credentials=True)

    # MongoDB
    mongo_client = MongoClient(os.getenv("MONGO_URI"))
    db = mongo_client[os.getenv("MONGO_DB_NAME")]
    app.db = db

    # Register blueprints
    from .routes.meals import meals_bp
    from .routes.users import users_bp
    from .routes.meals_history import meals_history_bp
    from .routes.auth import auth_bp
    from .routes.admin import admin_bp
    from .routes.favorites import favorites_bp
    from .routes.auto import auto_bp
    from .routes.stats import stats_bp
    from .routes.search import search_bp
    app.register_blueprint(meals_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(meals_history_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(favorites_bp)
    app.register_blueprint(auto_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(search_bp)

    return app
