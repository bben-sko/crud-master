from flask import blueprint, request, jsonify
from .moduls import db, Movie

inventory_bp = blueprint("inventory", __name__)

# Route to get all movies
@inventory_bp.route("/api/movies", methods=["GET", "POST", "DELETE"])
def movies():
    if request.method == "GET":
        movies = Movie.query.all()
        return jsonify([movie.to_dict() for movie in movies]), 200

    elif request.method == "POST":
        data = request.get_json()
        new_movie = Movie(title=data["title"], description=data["description"])
        db.session.add(new_movie)
        db.session.commit()
        return jsonify(new_movie.to_dict()), 201

    elif request.method == "DELETE":
        Movie.query.delete()
        db.session.commit()
        return jsonify({"message": "All movies deleted"}), 200

# Route to get, update, or delete a specific movie by ID
@inventory_bp.route("/api/movies/<int:movie_id>", methods=["GET", "PUT", "DELETE"])
def movie_by_id(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"error": "Movie not found"}), 404

    if request.method == "GET":
        return jsonify(movie.to_dict()), 200

    elif request.method == "PUT":
        data = request.get_json()
        movie.title = data["title"]
        movie.description = data["description"]
        db.session.commit()
        return jsonify(movie.to_dict()), 200

    elif request.method == "DELETE":
        db.session.delete(movie)
        db.session.commit()
        return jsonify({"message": "Movie deleted"}), 200