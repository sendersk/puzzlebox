"""Tests for PuzzleBox presentation helpers."""

from puzzlebox.models import Difficulty, Question, Quiz, QuizSession
from puzzlebox.presentation import display_question
from puzzlebox.runner import QuizRunner


def test_display_question(capsys) -> None:
    """Test that the current question is displayed correctly."""
    question = Question(
        text="What is Python?",
        answers=("Programming language", "Database"),
        correct_answer="Programming language",
        category="Programming",
        difficulty=Difficulty.EASY,
    )
    quiz = Quiz(questions=(question,))
    runner = QuizRunner(QuizSession(quiz))

    display_question(runner)

    captured = capsys.readouterr()

    assert "Question 1/1" in captured.out
    assert "What is Python?" in captured.out
    assert "1. Programming language" in captured.out
    assert "2. Database" in captured.out
