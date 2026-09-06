"""Question repository abstractions."""

import logging
from pathlib import Path
from typing import Protocol

from puzzlebox.models import Question
from puzzlebox.questions import load_questions

logger = logging.getLogger(__name__)


class QuestionRepository(Protocol):
    """Define the interface for question repositories."""

    def get_questions(self) -> tuple[Question, ...]:
        """Return all available questions."""


class JsonQuestionRepository:
    """Load questions from a JSON file."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def get_questions(self) -> tuple[Question, ...]:
        """Return quiz questions loaded from the configured JSON file."""
        logger.info("Fetching questions from repository: %s", self._path)
        return load_questions(self._path)
