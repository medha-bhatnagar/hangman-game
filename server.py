"""Flask server: Hangman REST API and browser client."""

from __future__ import annotations

import uuid

from flask import Flask, jsonify, request, send_from_directory

from game import HangmanGame, InvalidGuessError
from word_manager import InvalidDifficultyError, WordManager

VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def create_app(word_manager: WordManager | None = None) -> Flask:
    app = Flask(__name__, static_folder="static", static_url_path="/static")
    manager = word_manager or WordManager()
    games: dict[str, HangmanGame] = {}

    def game_payload(game_id: str, game: HangmanGame, *, include_id: bool = True) -> dict:
        payload = game.to_state()
        if include_id:
            payload = {"game_id": game_id, **payload}
        return payload

    @app.get("/")
    def index():
        return send_from_directory(app.static_folder, "index.html")

    @app.post("/api/games")
    def create_game():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "JSON body required"}), 400

        difficulty = data.get("difficulty")
        if not isinstance(difficulty, str) or difficulty.strip().lower() not in VALID_DIFFICULTIES:
            return jsonify({"error": "difficulty must be easy, medium, or hard"}), 400

        try:
            word = manager.random_word(difficulty)
        except InvalidDifficultyError as exc:
            return jsonify({"error": str(exc)}), 400

        game_id = uuid.uuid4().hex
        game = HangmanGame(word)
        games[game_id] = game
        return jsonify(game_payload(game_id, game)), 201

    @app.get("/api/games/<game_id>")
    def get_game(game_id: str):
        game = games.get(game_id)
        if game is None:
            return jsonify({"error": "game not found"}), 404
        return jsonify(game_payload(game_id, game)), 200

    @app.post("/api/games/<game_id>/guess")
    def guess_letter(game_id: str):
        game = games.get(game_id)
        if game is None:
            return jsonify({"error": "game not found"}), 404

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"error": "JSON body required"}), 400
        if "letter" not in data:
            return jsonify({"error": "letter is required"}), 400

        try:
            game.guess(data["letter"])
        except InvalidGuessError as exc:
            return jsonify({"error": str(exc)}), 400

        return jsonify(game_payload(game_id, game)), 200

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
