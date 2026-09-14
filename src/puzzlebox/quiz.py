"""Application services for quiz creation."""

import random

from puzzlebox.models import Question, Quiz
from puzzlebox.repositories import QuestionRepository


def create_quiz(
    repository: QuestionRepository,
    *,
    shuffle: bool = False,
) -> Quiz:
    """Create a quiz from repository questions."""
    questions = repository.get_questions()

    if shuffle:
        questions = shuffle_questions(questions)

    return Quiz(questions=questions)


def shuffle_questions(
    questions: tuple[Question, ...],
) -> tuple[Question, ...]:
    """Return questions in a randomized order."""
    shuffled = list(questions)
    random.shuffle(shuffled)
    return tuple(shuffled)
