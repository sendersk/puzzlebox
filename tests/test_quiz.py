"""Tests for quiz application services."""

import pytest

from puzzlebox.models import Difficulty, Question
from puzzlebox.quiz import create_quiz


class FakeQuestionRepository:
    """Provide a fixed set of questions for testing."""

    def __init__(self, questions: tuple[Question, ...]) -> None:
        self._questions = questions

    def get_questions(self) -> tuple[Question, ...]:
        """Return the configured questions."""
        return self._questions


def test_create_quiz_uses_repository_questions() -> None:
    """Test that create_quiz builds a quiz from repository questions."""
    question_one = Question(
        text="What is Python?",
        answers=("Language", "Database"),
        correct_answer="Language",
        category="Python",
        difficulty=Difficulty.EASY,
    )

    question_two = Question(
        text="What is a tuple?",
        answers=("Mutable", "Immutable"),
        correct_answer="Immutable",
        category="Python",
        difficulty=Difficulty.MEDIUM,
    )

    repository = FakeQuestionRepository(
        questions=(question_one, question_two),
    )

    quiz = create_quiz(repository)

    assert len(quiz) == 2
    assert quiz.questions == (question_one, question_two)


def test_create_quiz_rejects_empty_repository() -> None:
    """Test that creating a quiz without questions fails."""
    repository = FakeQuestionRepository(questions=())

    with pytest.raises(
        ValueError,
        match="A quiz must contain at least one question",
    ):
        create_quiz(repository)
