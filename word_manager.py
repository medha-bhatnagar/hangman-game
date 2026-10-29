"""Load difficulty-based word lists and pick a random word."""

from __future__ import annotations

import random
from pathlib import Path


class InvalidDifficultyError(ValueError):
    """Raised when a difficulty is missing or unknown."""


class WordManager:
    DIFFICULTIES = ("easy", "medium", "hard")

    def __init__(self, words_dir: str | Path | None = None) -> None:
        base = Path(words_dir) if words_dir else Path(__file__).resolve().parent / "words"
        self._words: dict[str, list[str]] = {}
        for difficulty in self.DIFFICULTIES:
            path = base / f"{difficulty}.txt"
            if not path.is_file():
                raise FileNotFoundError(f"missing word list: {path}")
            self._words[difficulty] = self._load_file(path)

    def random_word(self, difficulty: str) -> str:
        key = self._normalize_difficulty(difficulty)
        return random.choice(self._words[key])

    def words_for(self, difficulty: str) -> list[str]:
        key = self._normalize_difficulty(difficulty)
        return list(self._words[key])

    def _normalize_difficulty(self, difficulty: str) -> str:
        if not isinstance(difficulty, str):
            raise InvalidDifficultyError("difficulty must be a string")
        key = difficulty.strip().lower()
        if key not in self._words:
            raise InvalidDifficultyError(f"unknown difficulty: {difficulty}")
        return key

    @staticmethod
    def _load_file(path: Path) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for raw in path.read_text(encoding="utf-8").splitlines():
            word = raw.strip().lower()
            if not word:
                continue
            if not word.isascii() or not word.isalpha():
                raise ValueError(f"word must contain only English letters A-Z in {path.name}: {raw!r}")
            if word in seen:
                continue
            seen.add(word)
            ordered.append(word)
        if not ordered:
            raise ValueError(f"word list is empty: {path}")
        return ordered
