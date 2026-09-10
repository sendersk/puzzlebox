"""Tests for PuzzleBox presentation helpers."""

from puzzlebox.models import Difficulty, Question, Quiz, QuizSession
from puzzlebox.presentation import display_answer_result, display_question, display_quiz_result, get_answer
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


def test_get_answer_returns_valid_answer_number(
    monkeypatch,
) -> None:
    """Test that get_answer returns a valid answer number."""
    question = Question(
        text="What is Python?",
        answers=("Programming language", "Database"),
        correct_answer="Programming language",
        category="Programming",
        difficulty=Difficulty.EASY,
    )
    quiz = Quiz(questions=(question,))
    runner = QuizRunner(QuizSession(quiz))

    monkeypatch.setattr("builtins.input", lambda _: "2")

    answer = get_answer(runner)

    assert answer == 2


def test_get_answer_retries_after_non_numeric_input(
    monkeypatch,
    capsys,
) -> None:
    """Test that get_answer retries after non-numeric input."""
    question = Question(
        text="What is Python?",
        answers=("Programming language", "Database"),
        correct_answer="Programming language",
        category="Programming",
        difficulty=Difficulty.EASY,
    )
    quiz = Quiz(questions=(question,))
    runner = QuizRunner(QuizSession(quiz))

    answers = iter(("abc", "1"))
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    answer = get_answer(runner)

    captured = capsys.readouterr()

    assert answer == 1
    assert "Please enter a number." in captured.out


def test_get_answer_retries_after_invalid_answer_number(
    monkeypatch,
    capsys,
) -> None:
    """Test that get_answer retries after an out-of-range answer."""
    question = Question(
        text="What is Python?",
        answers=("Programming language", "Database"),
        correct_answer="Programming language",
        category="Programming",
        difficulty=Difficulty.EASY,
    )
    quiz = Quiz(questions=(question,))
    runner = QuizRunner(QuizSession(quiz))

    answers = iter(("3", "2"))
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    answer = get_answer(runner)

    captured = capsys.readouterr()

    assert answer == 2
    assert "Please select one of the available answers." in captured.out


def test_display_answer_result_shows_correct_message(
    capsys,
) -> None:
    """Test that a correct answer displays the correct message."""
    display_answer_result(True)

    captured = capsys.readouterr()

    assert captured.out == "Correct!\n"


def test_display_answer_result_shows_wrong_message(
    capsys,
) -> None:
    """Test that an incorrect answer displays the wrong message."""
    display_answer_result(False)

    captured = capsys.readouterr()

    assert captured.out == "Wrong!\n"


def test_display_quiz_result_shows_final_score(capsys) -> None:
    """Test that the final quiz result is displayed."""
    question = Question(
        text="What is 2 + 2?",
        answers=("3", "4"),
        correct_answer="4",
        category="Math",
        difficulty=Difficulty.EASY,
    )
    quiz = Quiz(questions=(question,))
    session = QuizSession(quiz)
    runner = QuizRunner(session)

    runner.answer("4")

    display_quiz_result(runner)

    captured = capsys.readouterr()

    assert captured.out == (
        "Quiz finished!\n"
        "Score: 1/1\n"
        "Percentage: 100.0%\n"
    )
