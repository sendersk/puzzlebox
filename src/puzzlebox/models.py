"""Domain models for PuzzleBox."""

from dataclasses import dataclass
from enum import StrEnum


class Difficulty(StrEnum):
    """Represent the difficulty level of a question."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True, slots=True)
class Question:
    """Represent a multiple-choice quiz question."""

    text: str
    answers: tuple[str, ...]
    correct_answer: str
    category: str
    difficulty: Difficulty

    def __post_init__(self) -> None:
        """Validate the question after initialization."""
        if not self.text.strip():
            raise ValueError("Question text cannot be empty.")

        if len(self.answers) < 2:
            raise ValueError("A question must have at least two answers.")

        if len(set(self.answers)) != len(self.answers):
            raise ValueError("Question answers must be unique.")

        if self.correct_answer not in self.answers:
            raise ValueError("Correct answer must be one of the available answers.")

        if not self.category.strip():
            raise ValueError("Question category cannot be empty.")