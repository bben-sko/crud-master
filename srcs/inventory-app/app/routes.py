from flask import Blueprint, jsonify, request

from .models import Movie, db


inventory_bp = Blueprint("inventory", __name__)


def validate_movie_payload(payload):
    if not isinstance(payload, dict):
        return "Request body must be a JSON object"

    title = payload.get("title")
    description = payload.get("description")

    if not isinstance(title, str) or not title.strip():
        return "Field 'title' is required and must be a non-empty string"

    if not isinstance(description, str) or not description.strip():
        return "Field 'description' is required and must be a non-empty string"

    return None


@inventory_bp.get("/health")
def health_check():
    return jsonify({"status": "ok", "service": "inventory-api"}), 200


@inventory_bp.route("/api/movies", methods=["GET", "POST", "DELETE"])
def movies():
    if request.method == "GET":
        title_filter = request.args.get("title")
        query = Movie.query.order_by(Movie.id.asc())

        if title_filter:
            query = query.filter(Movie.title.ilike(f"%{title_filter}%"))

        return jsonify([movie.to_dict() for movie in query.all()]), 200

    if request.method == "POST":
        payload = request.get_json(silent=True)
        validation_error = validate_movie_payload(payload)
        if validation_error:
            return jsonify({"error": validation_error}), 400

        movie = Movie(
            title=payload["title"].strip(),
            description=payload["description"].strip(),
        )
        db.session.add(movie)
        db.session.commit()
        return jsonify(movie.to_dict()), 201

    deleted_count = db.session.query(Movie).delete()
    db.session.commit()
    return jsonify({"message": "All movies deleted", "deleted": deleted_count}), 200


@inventory_bp.route("/api/movies/<int:movie_id>", methods=["GET", "PUT", "DELETE"])
def movie_by_id(movie_id):
    movie = db.session.get(Movie, movie_id)

    if movie is None:
        return jsonify({"error": "Movie not found"}), 404

    if request.method == "GET":
        return jsonify(movie.to_dict()), 200

    if request.method == "PUT":
        payload = request.get_json(silent=True)
        validation_error = validate_movie_payload(payload)
        if validation_error:
            return jsonify({"error": validation_error}), 400

        movie.title = payload["title"].strip()
        movie.description = payload["description"].strip()
        db.session.commit()
        return jsonify(movie.to_dict()), 200

    db.session.delete(movie)
    db.session.commit()
    return jsonify({"message": "Movie deleted", "id": movie_id}), 200
