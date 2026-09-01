"""Question repository abstractions."""

from pathlib import Path
from typing import Protocol

from puzzlebox.models import Question
from puzzlebox.questions import load_questions


class QuestionRepository(Protocol):
    """Define the interface for question repositories."""

    def get_questions(self) -> tuple[Question, ...]:
        """Return all available questions."""


class JsonQuestionRepository:
    """Load questions from a JSON file."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def get_questions(self) -> tuple[Question, ...]:
        """Return questions loaded from the JSON file."""
        return load_questions(self._path)
