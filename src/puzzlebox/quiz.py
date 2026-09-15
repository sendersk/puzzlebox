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


def filter_questions_by_category(
    questions: tuple[Question, ...],
    category: str | None,
) -> tuple[Question, ...]:
    """Return questions matching the given category."""
    if category is None:
        return questions

    normalized_category = category.strip().casefold()

    return tuple(
        question
        for question in questions
        if question.category.strip().casefold() == normalized_category
    )
