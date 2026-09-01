"""Application services for quiz creation."""

from puzzlebox.models import Quiz
from puzzlebox.repositories import QuestionRepository


def create_quiz(repository: QuestionRepository) -> Quiz:
    """Create a quiz from questions provided by a repository."""
    questions = repository.get_questions()

    return Quiz(questions=questions)
