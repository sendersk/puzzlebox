"""Tests for PuzzleBox domain models."""

import pytest

from puzzlebox.models import Difficulty, Question


def test_question_can_be_created() -> None:
    """Test creating a valid question."""
    question = Question(
        text="What is the output of 2 ** 3?",
        answers=("5", "6", "8", "9"),
        correct_answer="8",
        category="Python",
        difficulty=Difficulty.EASY,
    )

    assert question.text == "What is the output of 2 ** 3?"
    assert question.correct_answer == "8"
    assert question.difficulty is Difficulty.EASY


def test_question_rejects_empty_text() -> None:
    """Test that empty question text is rejected."""
    with pytest.raises(ValueError, match="Question text cannot be empty"):
        Question(
            text="   ",
            answers=("Yes", "No"),
            correct_answer="Yes",
            category="General",
            difficulty=Difficulty.EASY,
        )


def test_question_requires_at_least_two_answers() -> None:
    """Test that a question requires at least two answers."""
    with pytest.raises(
        ValueError,
        match="A question must have at least two answers",
    ):
        Question(
            text="Is Python a programming language?",
            answers=("Yes",),
            correct_answer="Yes",
            category="Programming",
            difficulty=Difficulty.EASY,
        )


def test_question_rejects_duplicate_answers() -> None:
    """Test that duplicate answers are rejected."""
    with pytest.raises(
        ValueError,
        match="Question answers must be unique",
    ):
        Question(
            text="Which number is correct?",
            answers=("1", "2", "2"),
            correct_answer="2",
            category="Math",
            difficulty=Difficulty.EASY,
        )


def test_question_requires_valid_correct_answer() -> None:
    """Test that the correct answer must exist in the answer list."""
    with pytest.raises(
        ValueError,
        match="Correct answer must be one of the available answers",
    ):
        Question(
            text="What is 2 + 2?",
            answers=("3", "4", "5"),
            correct_answer="6",
            category="Math",
            difficulty=Difficulty.EASY,
        )


def test_question_rejects_empty_category() -> None:
    """Test that an empty category is rejected."""
    with pytest.raises(
        ValueError,
        match="Question category cannot be empty",
    ):
        Question(
            text="What is Python?",
            answers=("Language", "Database"),
            correct_answer="Language",
            category=" ",
            difficulty=Difficulty.EASY,
        )