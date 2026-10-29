import tempfile
import unittest
from pathlib import Path

from server import create_app
from word_manager import WordManager


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        (root / "easy.txt").write_text("cat\n", encoding="utf-8")
        (root / "medium.txt").write_text("tiger\n", encoding="utf-8")
        (root / "hard.txt").write_text("elephant\n", encoding="utf-8")
        app = create_app(WordManager(root))
        app.config["TESTING"] = True
        self.client = app.test_client()

    def tearDown(self):
        self.temp.cleanup()

    def start(self, difficulty="easy"):
        response = self.client.post("/api/games", json={"difficulty": difficulty})
        self.assertEqual(response.status_code, 201)
        return response.get_json()

    def test_create_all_difficulties(self):
        for difficulty, length in (("easy", 3), ("medium", 5), ("hard", 8)):
            data = self.start(difficulty)
            self.assertEqual(data["status"], "playing")
            self.assertNotIn("word", data)
            self.assertEqual(len(data["pattern"].replace(" ", "")), length)

    def test_get_state_does_not_leak_word(self):
        created = self.start()
        response = self.client.get(f"/api/games/{created['game_id']}")
        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertNotIn("word", body)
        self.assertEqual(body["status"], "playing")

    def test_correct_and_incorrect_guesses(self):
        game_id = self.start()["game_id"]
        correct = self.client.post(f"/api/games/{game_id}/guess", json={"letter": "c"})
        self.assertEqual(correct.status_code, 200)
        self.assertEqual(correct.get_json()["pattern"], "c _ _")
        self.assertEqual(correct.get_json()["remaining_guesses"], 6)

        wrong = self.client.post(f"/api/games/{game_id}/guess", json={"letter": "z"})
        self.assertEqual(wrong.get_json()["remaining_guesses"], 5)
        self.assertIn("z", wrong.get_json()["incorrect_letters"])

    def test_duplicate_and_invalid_guesses(self):
        game_id = self.start()["game_id"]
        self.client.post(f"/api/games/{game_id}/guess", json={"letter": "c"})
        duplicate = self.client.post(f"/api/games/{game_id}/guess", json={"letter": "c"})
        self.assertEqual(duplicate.status_code, 400)

        invalid = self.client.post(f"/api/games/{game_id}/guess", json={"letter": "ab"})
        self.assertEqual(invalid.status_code, 400)

        missing = self.client.post(f"/api/games/{game_id}/guess", json={})
        self.assertEqual(missing.status_code, 400)

    def test_win_then_new_game(self):
        first = self.start()
        game_id = first["game_id"]
        self.client.post(f"/api/games/{game_id}/guess", json={"letter": "c"})
        self.client.post(f"/api/games/{game_id}/guess", json={"letter": "a"})
        won = self.client.post(f"/api/games/{game_id}/guess", json={"letter": "t"})
        body = won.get_json()
        self.assertEqual(body["status"], "won")
        self.assertEqual(body["word"], "cat")

        after = self.client.post(f"/api/games/{game_id}/guess", json={"letter": "z"})
        self.assertEqual(after.status_code, 400)

        second = self.start("medium")
        self.assertNotEqual(second["game_id"], game_id)
        self.assertEqual(second["status"], "playing")
        self.assertNotIn("word", second)

    def test_loss_reveals_word(self):
        game_id = self.start()["game_id"]
        for letter in "bdefgh":
            response = self.client.post(
                f"/api/games/{game_id}/guess", json={"letter": letter}
            )
        body = response.get_json()
        self.assertEqual(body["status"], "lost")
        self.assertEqual(body["word"], "cat")
        self.assertEqual(body["remaining_guesses"], 0)

    def test_unknown_game_and_bad_create(self):
        missing = self.client.get("/api/games/does-not-exist")
        self.assertEqual(missing.status_code, 404)

        bad = self.client.post("/api/games", json={"difficulty": "impossible"})
        self.assertEqual(bad.status_code, 400)

        empty = self.client.post("/api/games", data="not-json", content_type="text/plain")
        self.assertEqual(empty.status_code, 400)

    def test_games_are_isolated(self):
        a = self.start()["game_id"]
        b = self.start()["game_id"]
        self.client.post(f"/api/games/{a}/guess", json={"letter": "c"})
        state_b = self.client.get(f"/api/games/{b}").get_json()
        self.assertEqual(state_b["pattern"], "_ _ _")

    def test_index_serves_browser_client(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)
        self.assertIn("Hangman", html)
        self.assertIn("/static/app.js", html)


if __name__ == "__main__":
    unittest.main()
