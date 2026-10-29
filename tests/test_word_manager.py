import tempfile
import unittest
from pathlib import Path

from word_manager import InvalidDifficultyError, WordManager


class WordManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        (root / "easy.txt").write_text("cat\n dog \nCAT\nice\n\n", encoding="utf-8")
        (root / "medium.txt").write_text("tiger\n", encoding="utf-8")
        (root / "hard.txt").write_text("elephant\n", encoding="utf-8")
        self.manager = WordManager(root)

    def tearDown(self):
        self.temp.cleanup()

    def test_loads_and_deduplicates(self):
        self.assertEqual(self.manager.words_for("easy"), ["cat", "dog", "ice"])

    def test_random_word_from_difficulty(self):
        self.assertEqual(self.manager.random_word("MEDIUM"), "tiger")

    def test_invalid_difficulty(self):
        with self.assertRaises(InvalidDifficultyError):
            self.manager.random_word("expert")

    def test_rejects_non_alphabetic_words(self):
        root = Path(self.temp.name)
        (root / "easy.txt").write_text("ok\nbad-word\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            WordManager(root)

    def test_project_word_lists_load(self):
        manager = WordManager()
        for difficulty in ("easy", "medium", "hard"):
            words = manager.words_for(difficulty)
            self.assertGreater(len(words), 20)
            self.assertTrue(all(w.isascii() and w.isalpha() and w == w.lower() for w in words))


if __name__ == "__main__":
    unittest.main()
