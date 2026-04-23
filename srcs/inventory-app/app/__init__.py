import os

from dotenv import load_dotenv
from flask import Flask

from .models import db


load_dotenv()


def build_database_url():
    configured_url = os.getenv("INVENTORY_DB_URL")
    if configured_url:
        return configured_url

    user = os.getenv("INVENTORY_DB_USER", "inventory_user")
    password = os.getenv("INVENTORY_DB_PASSWORD", "inventory_pass")
    host = os.getenv("INVENTORY_DB_HOST", "localhost")
    port = os.getenv("INVENTORY_DB_PORT", "5432")
    database = os.getenv("INVENTORY_DB_NAME", "movies_db")
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def create_app():
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=build_database_url(),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
    )

    db.init_app(app)

    from .routes import inventory_bp

    app.register_blueprint(inventory_bp)

    with app.app_context():
        db.create_all()

    return app
