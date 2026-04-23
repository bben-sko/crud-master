import os

from dotenv import load_dotenv
from flask import Flask

from .routes import api_gateway_bp


load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config.update(
        INVENTORY_API_URL=os.getenv("INVENTORY_API_URL", "http://localhost:8080"),
        INVENTORY_TIMEOUT=int(os.getenv("INVENTORY_TIMEOUT", "10")),
        RABBITMQ_HOST=os.getenv("RABBITMQ_HOST", "localhost"),
        RABBITMQ_PORT=int(os.getenv("RABBITMQ_PORT", "5672")),
        RABBITMQ_USER=os.getenv("RABBITMQ_USER", "guest"),
        RABBITMQ_PASSWORD=os.getenv("RABBITMQ_PASSWORD", "guest"),
        RABBITMQ_QUEUE=os.getenv("RABBITMQ_QUEUE", "billing_queue"),
    )
    app.register_blueprint(api_gateway_bp)
    return app
