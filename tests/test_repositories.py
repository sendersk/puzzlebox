"""Tests for question repositories."""

from pathlib import Path

from puzzlebox.models import Question
from puzzlebox.repositories import JsonQuestionRepository, QuestionRepository


def test_json_question_repository_returns_questions(
    tmp_path: Path,
) -> None:
    """Test that the JSON repository returns loaded questions."""
    questions_file = tmp_path / "questions.json"

    questions_file.write_text(
        """
        {
            "questions": [
                {
                    "text": "What is Python?",
                    "answers": ["Language", "Database"],
                    "correct_answer": "Language",
                    "category": "Python",
                    "difficulty": "easy"
                }
            ]
        }
        """,
        encoding="utf-8",
    )

    repository = JsonQuestionRepository(questions_file)

    questions = repository.get_questions()

    assert len(questions) == 1
    assert questions[0].text == "What is Python?"


class FakeQuestionRepository:
    """Provide questions for testing."""

    def get_questions(self) -> tuple[Question, ...]:
        """Return an empty question collection."""
        return ()


def test_fake_repository_matches_protocol() -> None:
    """Test that a compatible repository satisfies the protocol."""
    repository: QuestionRepository = FakeQuestionRepository()

    assert repository.get_questions() == ()


def test_json_repository_matches_protocol() -> None:
    """Test that the JSON repository satisfies the protocol."""
    repository: QuestionRepository = JsonQuestionRepository(
        Path("resources/questions.json")
    )

    assert repository.get_questions()
