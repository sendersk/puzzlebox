"""Application services for quiz creation."""

import random

from puzzlebox.models import Difficulty, Question, Quiz
from puzzlebox.repositories import QuestionRepository


def create_quiz(
    repository: QuestionRepository,
    *,
    category: str | None = None,
    difficulty: Difficulty | None = None,
    shuffle: bool = False,
) -> Quiz:
    """Create a quiz from repository questions."""
    questions = repository.get_questions()

    questions = filter_questions_by_category(
        questions,
        category,
    )

    questions = filter_questions_by_difficulty(
        questions,
        difficulty,
    )

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


def filter_questions_by_difficulty(
    questions: tuple[Question, ...],
    difficulty: Difficulty | None,
) -> tuple[Question, ...]:
    """Filter questions by difficulty."""
    if difficulty is None:
        return questions

    return tuple(
        question
        for question in questions
        if question.difficulty == difficulty
    )
