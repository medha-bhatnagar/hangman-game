"""Hangman game engine. Independent of Flask and any user interface."""

from __future__ import annotations


class InvalidGuessError(ValueError):
    """Raised when a guess is invalid, duplicated, or submitted after the game ends."""


class HangmanGame:
    MAX_INCORRECT_GUESSES = 6

    def __init__(self, word: str, max_incorrect_guesses: int = MAX_INCORRECT_GUESSES) -> None:
        if not isinstance(word, str) or not word or not word.isascii() or not word.isalpha():
            raise ValueError("word must contain only English letters A-Z")
        if isinstance(max_incorrect_guesses, bool) or not isinstance(max_incorrect_guesses, int) or max_incorrect_guesses < 1:
            raise ValueError("max_incorrect_guesses must be a positive integer")

        self._word = word.lower()
        self._max_incorrect_guesses = max_incorrect_guesses
        self._guessed_letters: list[str] = []
        self._incorrect_letters: list[str] = []
        self._status = "playing"

    @property
    def word(self) -> str:
        return self._word

    def guess(self, letter: str) -> dict:
        if self._status != "playing":
            raise InvalidGuessError("game is already over")
        if not isinstance(letter, str):
            raise InvalidGuessError("guess must be a single letter")

        normalized = letter.lower()
        if len(normalized) != 1 or not normalized.isascii() or not normalized.isalpha():
            raise InvalidGuessError("guess must be a single English letter A-Z")
        if normalized in self._guessed_letters:
            raise InvalidGuessError("letter has already been guessed")

        self._guessed_letters.append(normalized)
        if normalized in self._word:
            if all(ch in self._guessed_letters for ch in self._word):
                self._status = "won"
        else:
            self._incorrect_letters.append(normalized)
            if self._remaining_guesses() == 0:
                self._status = "lost"

        return self.to_state()

    def to_state(self) -> dict:
        state = {
            "pattern": self._pattern(),
            "guessed_letters": list(self._guessed_letters),
            "incorrect_letters": list(self._incorrect_letters),
            "remaining_guesses": self._remaining_guesses(),
            "status": self._status,
        }
        if self._status in {"won", "lost"}:
            state["word"] = self._word
        return state

    def _pattern(self) -> str:
        return " ".join(ch if ch in self._guessed_letters else "_" for ch in self._word)

    def _remaining_guesses(self) -> int:
        return self._max_incorrect_guesses - len(self._incorrect_letters)
