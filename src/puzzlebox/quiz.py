"""Application services for quiz creation."""

import random

from puzzlebox.models import Question, Quiz
from puzzlebox.repositories import QuestionRepository


def create_quiz(repository: QuestionRepository) -> Quiz:
    """Create a quiz from questions provided by a repository."""
    questions = repository.get_questions()

    return Quiz(questions=questions)


def shuffle_questions(
    questions: tuple[Question, ...],
) -> tuple[Question, ...]:
    """Return questions in a randomized order."""
    shuffled = list(questions)
    random.shuffle(shuffled)
    return tuple(shuffled)
