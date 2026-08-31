"""Tests for question data loading."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from puzzlebox.models import Difficulty
from puzzlebox.questions import load_questions


def test_load_questions_from_json(tmp_path: Path) -> None:
    """Test loading valid questions from a JSON file."""
    questions_file = tmp_path / "questions.json"

    questions_file.write_text(
        """
        {
            "questions": [
                {
                    "text": "What is 2 + 2?",
                    "answers": ["3", "4", "5"],
                    "correct_answer": "4",
                    "category": "Math",
                    "difficulty": "easy"
                }
            ]
        }
        """,
        encoding="utf-8",
    )

    questions = load_questions(questions_file)

    assert len(questions) == 1
    assert questions[0].text == "What is 2 + 2?"
    assert questions[0].answers == ("3", "4", "5")
    assert questions[0].correct_answer == "4"
    assert questions[0].category == "Math"
    assert questions[0].difficulty is Difficulty.EASY


def test_load_questions_rejects_invalid_difficulty(
    tmp_path: Path,
) -> None:
    """Test that an invalid difficulty is rejected."""
    questions_file = tmp_path / "questions.json"

    questions_file.write_text(
        """
        {
            "questions": [
                {
                    "text": "What is 2 + 2?",
                    "answers": ["3", "4"],
                    "correct_answer": "4",
                    "category": "Math",
                    "difficulty": "impossible"
                }
            ]
        }
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_questions(questions_file)


def test_load_questions_rejects_unknown_fields(
    tmp_path: Path,
) -> None:
    """Test that unknown question fields are rejected."""
    questions_file = tmp_path / "questions.json"

    questions_file.write_text(
        """
        {
            "questions": [
                {
                    "text": "What is 2 + 2?",
                    "answers": ["3", "4"],
                    "correct_answer": "4",
                    "category": "Math",
                    "difficulty": "easy",
                    "unknown": true
                }
            ]
        }
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_questions(questions_file)


def test_load_questions_rejects_missing_required_field(
    tmp_path: Path,
) -> None:
    """Test that missing required fields are rejected."""
    questions_file = tmp_path / "questions.json"

    questions_file.write_text(
        """
        {
            "questions": [
                {
                    "text": "What is 2 + 2?",
                    "answers": ["3", "4"],
                    "category": "Math",
                    "difficulty": "easy"
                }
            ]
        }
        """,
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_questions(questions_file)
