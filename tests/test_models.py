"""Tests for PuzzleBox domain models."""

import pytest

from puzzlebox.models import Difficulty, Question, Quiz


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


def create_question(number: int) -> Question:
    """Create a test question with a unique value."""
    return Question(
        text=f"Question {number}",
        answers=("A", "B", "C"),
        correct_answer="A",
        category="Test",
        difficulty=Difficulty.EASY,
    )


def test_quiz_can_be_created() -> None:
    """Test creating a quiz with questions."""
    question_one = create_question(1)
    question_two = create_question(2)

    quiz = Quiz(questions=(question_one, question_two))

    assert len(quiz) == 2
    assert quiz.questions == (question_one, question_two)


def test_quiz_returns_question_by_index() -> None:
    """Test retrieving a question by index."""
    question_one = create_question(1)
    question_two = create_question(2)

    quiz = Quiz(questions=(question_one, question_two))

    assert quiz.get_question(0) is question_one
    assert quiz.get_question(1) is question_two


def test_quiz_rejects_empty_questions() -> None:
    """Test that an empty quiz is rejected."""
    with pytest.raises(
        ValueError,
        match="A quiz must contain at least one question",
    ):
        Quiz(questions=())


def test_quiz_rejects_invalid_question_index() -> None:
    """Test that an invalid question index raises an error."""
    quiz = Quiz(questions=(create_question(1),))

    with pytest.raises(
        IndexError,
        match="Question index out of range: 5",
    ):
        quiz.get_question(5)
