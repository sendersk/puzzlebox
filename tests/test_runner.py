"""Tests for the quiz runner."""

from puzzlebox.models import Difficulty, Question, Quiz, QuizSession
from puzzlebox.runner import QuizRunner


def create_quiz() -> Quiz:
    """Create a quiz for runner tests."""
    return Quiz(
        questions=(
            Question(
                text="What is 2 + 2?",
                answers=("3", "4", "5"),
                correct_answer="4",
                category="Math",
                difficulty=Difficulty.EASY,
            ),
            Question(
                text="What is 3 + 3?",
                answers=("5", "6", "7"),
                correct_answer="6",
                category="Math",
                difficulty=Difficulty.EASY,
            ),
        )
    )


def test_runner_returns_current_question_view() -> None:
    """Test that the runner exposes presentation-ready question data."""
    session = QuizSession(create_quiz())
    runner = QuizRunner(session)

    question = runner.current_question

    assert question.number == 1
    assert question.total == 2
    assert question.text == "What is 2 + 2?"
    assert question.answers == ("3", "4", "5")


def test_runner_submits_answer() -> None:
    """Test that the runner delegates answer submission."""
    session = QuizSession(create_quiz())
    runner = QuizRunner(session)

    result = runner.answer("4")

    assert result is True
    assert session.score == 1
    assert session.answered_count == 1


def test_runner_moves_to_next_question() -> None:
    """Test that the runner advances the session."""
    session = QuizSession(create_quiz())
    runner = QuizRunner(session)

    runner.answer("4")
    runner.next_question()

    question = runner.current_question

    assert question.number == 2
    assert question.text == "What is 3 + 3?"
