import unittest

from game import HangmanGame, InvalidGuessError


class HangmanGameTests(unittest.TestCase):
    def test_initial_state_hides_word(self):
        game = HangmanGame("eagle")
        state = game.to_state()
        self.assertEqual(state["pattern"], "_ _ _ _ _")
        self.assertEqual(state["remaining_guesses"], 6)
        self.assertEqual(state["status"], "playing")
        self.assertNotIn("word", state)
        self.assertNotIn("eagle", str(state))

    def test_correct_guess_does_not_cost_a_life(self):
        game = HangmanGame("eagle")
        state = game.guess("e")
        self.assertEqual(state["pattern"], "e _ _ _ e")
        self.assertEqual(state["remaining_guesses"], 6)
        self.assertEqual(state["guessed_letters"], ["e"])
        self.assertEqual(state["incorrect_letters"], [])

    def test_incorrect_guess_decrements_remaining(self):
        game = HangmanGame("eagle")
        state = game.guess("z")
        self.assertEqual(state["remaining_guesses"], 5)
        self.assertEqual(state["incorrect_letters"], ["z"])

    def test_duplicate_guess_is_rejected(self):
        game = HangmanGame("eagle")
        game.guess("e")
        with self.assertRaises(InvalidGuessError):
            game.guess("e")

    def test_invalid_guesses_are_rejected(self):
        game = HangmanGame("eagle")
        for bad in ("", "ee", "1", "!", " ", "é", "λ"):
            with self.assertRaises(InvalidGuessError):
                game.guess(bad)

    def test_guesses_are_case_insensitive(self):
        game = HangmanGame("Eagle")
        state = game.guess("E")
        self.assertEqual(state["pattern"], "e _ _ _ e")

    def test_win_reveals_word(self):
        game = HangmanGame("hi")
        game.guess("h")
        state = game.guess("i")
        self.assertEqual(state["status"], "won")
        self.assertEqual(state["word"], "hi")
        self.assertEqual(state["pattern"], "h i")

    def test_loss_reveals_word(self):
        game = HangmanGame("hi", max_incorrect_guesses=2)
        game.guess("a")
        state = game.guess("b")
        self.assertEqual(state["status"], "lost")
        self.assertEqual(state["word"], "hi")
        self.assertEqual(state["remaining_guesses"], 0)

    def test_no_guesses_after_game_ends(self):
        game = HangmanGame("hi")
        game.guess("h")
        game.guess("i")
        with self.assertRaises(InvalidGuessError):
            game.guess("z")

    def test_rejects_non_alpha_word(self):
        for word in ("ice-cream", "café", "猫"):
            with self.subTest(word=word), self.assertRaises(ValueError):
                HangmanGame(word)

    def test_rejects_invalid_guess_limit(self):
        for limit in (0, -1, 1.5, "6", True):
            with self.subTest(limit=limit), self.assertRaises(ValueError):
                HangmanGame("cat", max_incorrect_guesses=limit)


if __name__ == "__main__":
    unittest.main()
