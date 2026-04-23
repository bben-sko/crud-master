import json

import pika
import requests
from flask import Blueprint, Response, current_app, jsonify, request


api_gateway_bp = Blueprint("api_gateway", __name__)


def build_rabbitmq_parameters():
    credentials = pika.PlainCredentials(
        current_app.config["RABBITMQ_USER"],
        current_app.config["RABBITMQ_PASSWORD"],
    )
    return pika.ConnectionParameters(
        host=current_app.config["RABBITMQ_HOST"],
        port=current_app.config["RABBITMQ_PORT"],
        credentials=credentials,
    )


def proxy_inventory_request(path):
    inventory_url = current_app.config["INVENTORY_API_URL"].rstrip("/")
    headers = {}

    if request.content_type:
        headers["Content-Type"] = request.content_type

    try:
        upstream_response = requests.request(
            method=request.method,
            url=f"{inventory_url}{path}",
            params=request.args,
            data=request.get_data(),
            headers=headers,
            timeout=current_app.config["INVENTORY_TIMEOUT"],
        )
    except requests.RequestException as exc:
        return jsonify({"error": "Inventory API unavailable", "details": str(exc)}), 503

    excluded_headers = {
        "connection",
        "content-encoding",
        "content-length",
        "transfer-encoding",
    }
    response_headers = [
        (key, value)
        for key, value in upstream_response.headers.items()
        if key.lower() not in excluded_headers
    ]

    return Response(
        upstream_response.content,
        status=upstream_response.status_code,
        headers=response_headers,
    )




@api_gateway_bp.route("/api/movies", methods=["GET", "POST", "DELETE"])
def movies():
    return proxy_inventory_request("/api/movies")


@api_gateway_bp.route("/api/movies/<int:movie_id>", methods=["GET", "PUT", "DELETE"])
def movie_detail(movie_id):
    return proxy_inventory_request(f"/api/movies/{movie_id}")


@api_gateway_bp.post("/api/billing")
def billing():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    try:
        connection = pika.BlockingConnection(build_rabbitmq_parameters())
        channel = connection.channel()
        channel.queue_declare(
            queue=current_app.config["RABBITMQ_QUEUE"],
            durable=True,
        )
        channel.basic_publish(
            exchange="",
            routing_key=current_app.config["RABBITMQ_QUEUE"],
            body=json.dumps(payload),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
    except pika.exceptions.AMQPError as exc:
        return jsonify({"error": "Failed to publish billing message", "details": str(exc)}), 503

    return jsonify({"message": "Message posted"}), 202
