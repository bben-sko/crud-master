from flask import Flask
from .moduls import db
from .routes import inventory_bp
import os
from dotenv import load_dotenv
load_dotenv()

db_url = os.getenv("INVENTORY_DB_URL")

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(inventory_bp)
    return app