"""Tests for quiz application services."""

import pytest

from puzzlebox.models import Difficulty, Question
from puzzlebox.quiz import create_quiz, shuffle_questions, filter_questions_by_category


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
