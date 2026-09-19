"""Tests for quiz application services."""

from unittest.mock import Mock

import pytest

from puzzlebox.models import Difficulty, Question
from puzzlebox.quiz import (
    create_quiz,
    filter_questions_by_category,
    filter_questions_by_difficulty,
    shuffle_questions,
)


class FakeQuestionRepository:
    """Provide a fixed set of questions for testing."""

    def __init__(self, questions: tuple[Question, ...]) -> None:
        self._questions = questions

    def get_questions(self) -> tuple[Question, ...]:
        """Return the configured questions."""
        return self._questions


def test_create_quiz_uses_repository_questions() -> None:
    """Test that create_quiz builds a quiz from repository questions."""
    question_one = Question(
        text="What is Python?",
        answers=("Language", "Database"),
        correct_answer="Language",
        category="Python",
        difficulty=Difficulty.EASY,
    )

    question_two = Question(
        text="What is a tuple?",
        answers=("Mutable", "Immutable"),
        correct_answer="Immutable",
        category="Python",
        difficulty=Difficulty.MEDIUM,
    )

    repository = FakeQuestionRepository(
        questions=(question_one, question_two),
    )

    quiz = create_quiz(repository)

    assert len(quiz) == 2
    assert quiz.questions == (question_one, question_two)


def test_create_quiz_rejects_empty_repository() -> None:
    """Test that creating a quiz without questions fails."""
    repository = FakeQuestionRepository(questions=())

    with pytest.raises(
        ValueError,
        match="A quiz must contain at least one question",
    ):
        create_quiz(repository)


def test_shuffle_questions_returns_same_questions_in_random_order() -> None:
    """Test that shuffling preserves all questions."""
    questions = (
        Question(
            text="Question 1",
            answers=("A", "B"),
            correct_answer="A",
            category="Test",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="Question 2",
            answers=("C", "D"),
            correct_answer="C",
            category="Test",
            difficulty=Difficulty.MEDIUM,
        ),
        Question(
            text="Question 3",
            answers=("E", "F"),
            correct_answer="E",
            category="Test",
            difficulty=Difficulty.HARD,
        ),
    )

    shuffled = shuffle_questions(questions)

    assert isinstance(shuffled, tuple)
    assert len(shuffled) == len(questions)
    assert set(shuffled) == set(questions)


def test_shuffle_questions_does_not_modify_original_questions() -> None:
    """Test that shuffling does not modify the original questions."""
    questions = (
        Question(
            text="Question 1",
            answers=("A", "B"),
            correct_answer="A",
            category="Test",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="Question 2",
            answers=("C", "D"),
            correct_answer="C",
            category="Test",
            difficulty=Difficulty.MEDIUM,
        ),
    )

    original_questions = questions

    shuffle_questions(questions)

    assert questions == original_questions


def test_create_quiz_does_not_shuffle_questions_by_default() -> None:
    """Test that quiz creation preserves question order by default."""
    questions = (
        Question(
            text="Question 1",
            answers=("A", "B"),
            correct_answer="A",
            category="Test",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="Question 2",
            answers=("A", "B"),
            correct_answer="B",
            category="Test",
            difficulty=Difficulty.MEDIUM,
        ),
    )

    repository = FakeQuestionRepository(questions)

    quiz = create_quiz(repository)

    assert quiz.questions == questions


def test_create_quiz_shuffles_questions_when_requested(
    monkeypatch,
) -> None:
    """Test that quiz creation shuffles questions when requested."""
    questions = (
        Question(
            text="Question 1",
            answers=("A", "B"),
            correct_answer="A",
            category="Test",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="Question 2",
            answers=("A", "B"),
            correct_answer="B",
            category="Test",
            difficulty=Difficulty.MEDIUM,
        ),
        Question(
            text="Question 3",
            answers=("A", "B"),
            correct_answer="A",
            category="Test",
            difficulty=Difficulty.HARD,
        ),
    )

    repository = FakeQuestionRepository(questions)

    def fake_shuffle(
        questions_to_shuffle: tuple[Question, ...],
    ) -> tuple[Question, ...]:
        return tuple(reversed(questions_to_shuffle))

    monkeypatch.setattr("puzzlebox.quiz.shuffle_questions", fake_shuffle)

    quiz = create_quiz(repository, shuffle=True)

    assert quiz.questions == tuple(reversed(questions))


def test_filter_questions_by_category_returns_matching_questions() -> None:
    """Test that only questions from the requested category are returned."""
    questions = (
        Question(
            text="What is 2 + 2?",
            answers=("3", "4"),
            correct_answer="4",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="What is Python?",
            answers=("Language", "Database"),
            correct_answer="Language",
            category="Programming",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="What is 3 + 3?",
            answers=("5", "6"),
            correct_answer="6",
            category="Math",
            difficulty=Difficulty.MEDIUM,
        ),
    )

    result = filter_questions_by_category(questions, "Math")

    assert result == (questions[0], questions[2])


def test_filter_questions_by_category_is_case_insensitive() -> None:
    """Test that category matching ignores letter case."""
    question = Question(
        text="What is 2 + 2?",
        answers=("3", "4"),
        correct_answer="4",
        category="Math",
        difficulty=Difficulty.EASY,
    )

    result = filter_questions_by_category((question,), "math")

    assert result == (question,)


def test_filter_questions_by_category_ignores_surrounding_whitespace() -> None:
    """Test that surrounding whitespace is ignored when matching categories."""
    question = Question(
        text="What is 2 + 2?",
        answers=("3", "4"),
        correct_answer="4",
        category="Math",
        difficulty=Difficulty.EASY,
    )

    result = filter_questions_by_category((question,), "  Math  ")

    assert result == (question,)


def test_filter_questions_by_category_returns_all_questions_when_category_is_none() -> None:
    """Test that no category filter returns the original questions."""
    questions = (
        Question(
            text="What is 2 + 2?",
            answers=("3", "4"),
            correct_answer="4",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="What is Python?",
            answers=("Language", "Database"),
            correct_answer="Language",
            category="Programming",
            difficulty=Difficulty.EASY,
        ),
    )

    result = filter_questions_by_category(questions, None)

    assert result == questions


def test_filter_questions_by_category_returns_empty_tuple_for_unknown_category() -> None:
    """Test that an unknown category produces no questions."""
    question = Question(
        text="What is 2 + 2?",
        answers=("3", "4"),
        correct_answer="4",
        category="Math",
        difficulty=Difficulty.EASY,
    )

    result = filter_questions_by_category((question,), "Science")

    assert result == ()


def test_create_quiz_filters_questions_by_category() -> None:
    """Test that create_quiz includes only questions from the requested category."""
    questions = (
        Question(
            text="What is 2 + 2?",
            answers=("3", "4"),
            correct_answer="4",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="What is Python?",
            answers=("Language", "Database"),
            correct_answer="Language",
            category="Programming",
            difficulty=Difficulty.EASY,
        ),
    )

    repository = Mock()
    repository.get_questions.return_value = questions

    quiz = create_quiz(repository, category="Math")

    assert quiz.questions == (questions[0],)


def test_create_quiz_without_category_includes_all_questions() -> None:
    """Test that create_quiz includes all questions when no category is given."""
    questions = (
        Question(
            text="What is 2 + 2?",
            answers=("3", "4"),
            correct_answer="4",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="What is Python?",
            answers=("Language", "Database"),
            correct_answer="Language",
            category="Programming",
            difficulty=Difficulty.EASY,
        ),
    )

    repository = Mock()
    repository.get_questions.return_value = questions

    quiz = create_quiz(repository)

    assert quiz.questions == questions


def test_create_quiz_applies_category_filter_before_shuffle(
    monkeypatch,
) -> None:
    """Test that category filtering happens before question shuffling."""
    questions = (
        Question(
            text="What is 2 + 2?",
            answers=("3", "4"),
            correct_answer="4",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="What is Python?",
            answers=("Language", "Database"),
            correct_answer="Language",
            category="Programming",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="What is 3 + 3?",
            answers=("5", "6"),
            correct_answer="6",
            category="Math",
            difficulty=Difficulty.MEDIUM,
        ),
    )

    repository = Mock()
    repository.get_questions.return_value = questions

    def fake_shuffle(
        filtered_questions: tuple[Question, ...],
    ) -> tuple[Question, ...]:
        assert filtered_questions == (questions[0], questions[2])
        return tuple(reversed(filtered_questions))

    monkeypatch.setattr(
        "puzzlebox.quiz.shuffle_questions",
        fake_shuffle,
    )

    quiz = create_quiz(
        repository,
        category="Math",
        shuffle=True,
    )

    assert quiz.questions == (questions[2], questions[0])


def test_filter_questions_by_difficulty() -> None:
    """Test that only questions with the requested difficulty are returned."""
    questions = (
        Question(
            text="Easy question",
            answers=("A", "B"),
            correct_answer="A",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="Hard question",
            answers=("A", "B"),
            correct_answer="B",
            category="Math",
            difficulty=Difficulty.HARD,
        ),
        Question(
            text="Another hard question",
            answers=("A", "B"),
            correct_answer="A",
            category="Science",
            difficulty=Difficulty.HARD,
        ),
    )

    result = filter_questions_by_difficulty(
        questions,
        Difficulty.HARD,
    )

    assert result == (questions[1], questions[2])


def test_filter_questions_by_difficulty_returns_all_when_not_configured() -> None:
    """Test that no filtering occurs when difficulty is None."""
    questions = (
        Question(
            text="Easy question",
            answers=("A", "B"),
            correct_answer="A",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="Hard question",
            answers=("A", "B"),
            correct_answer="B",
            category="Math",
            difficulty=Difficulty.HARD,
        ),
    )

    result = filter_questions_by_difficulty(questions, None)

    assert result == questions


def test_filter_questions_by_difficulty_returns_empty_when_no_match() -> None:
    """Test that an unmatched difficulty returns no questions."""
    questions = (
        Question(
            text="Easy question",
            answers=("A", "B"),
            correct_answer="A",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
    )

    result = filter_questions_by_difficulty(
        questions,
        Difficulty.HARD,
    )

    assert result == ()


def test_create_quiz_filters_by_difficulty() -> None:
    """Test that quiz creation filters questions by difficulty."""
    questions = (
        Question(
            text="Easy question",
            answers=("A", "B"),
            correct_answer="A",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="Hard question",
            answers=("A", "B"),
            correct_answer="B",
            category="Math",
            difficulty=Difficulty.HARD,
        ),
    )

    repository = Mock()
    repository.get_questions.return_value = questions

    quiz = create_quiz(
        repository,
        difficulty=Difficulty.HARD,
    )

    assert quiz.questions == (questions[1],)


def test_create_quiz_filters_by_category_and_difficulty_before_shuffle(
    monkeypatch,
) -> None:
    """Test that filters are applied before questions are shuffled."""
    questions = (
        Question(
            text="Easy math",
            answers=("A", "B"),
            correct_answer="A",
            category="Math",
            difficulty=Difficulty.EASY,
        ),
        Question(
            text="Hard math",
            answers=("A", "B"),
            correct_answer="B",
            category="Math",
            difficulty=Difficulty.HARD,
        ),
        Question(
            text="Hard science",
            answers=("A", "B"),
            correct_answer="A",
            category="Science",
            difficulty=Difficulty.HARD,
        ),
    )

    repository = Mock()
    repository.get_questions.return_value = questions

    def fake_shuffle(
        filtered_questions: tuple[Question, ...],
    ) -> tuple[Question, ...]:
        assert filtered_questions == (questions[1],)
        return filtered_questions

    monkeypatch.setattr(
        "puzzlebox.quiz.shuffle_questions",
        fake_shuffle,
    )

    quiz = create_quiz(
        repository,
        category="Math",
        difficulty=Difficulty.HARD,
        shuffle=True,
    )

    assert quiz.questions == (questions[1],)
