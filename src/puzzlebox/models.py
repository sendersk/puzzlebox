"""Domain models for PuzzleBox."""

from dataclasses import dataclass
from enum import StrEnum


class Difficulty(StrEnum):
    """Represent the difficulty level of a question."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass(frozen=True, slots=True)
class Question:
    """Represent a multiple-choice quiz question."""

    text: str
    answers: tuple[str, ...]
    correct_answer: str
    category: str
    difficulty: Difficulty

    def __post_init__(self) -> None:
        """Validate the question after initialization."""
        if not self.text.strip():
            raise ValueError("Question text cannot be empty.")

        if len(self.answers) < 2:
            raise ValueError("A question must have at least two answers.")

        if len(set(self.answers)) != len(self.answers):
            raise ValueError("Question answers must be unique.")

        if self.correct_answer not in self.answers:
            raise ValueError("Correct answer must be one of the available answers.")

        if not self.category.strip():
            raise ValueError("Question category cannot be empty.")


@dataclass(frozen=True, slots=True)
class Quiz:
    """Represent a collection of quiz questions."""

    questions: tuple[Question, ...]

    def __post_init__(self) -> None:
        """Validate the quiz after initialization."""
        if not self.questions:
            raise ValueError("A quiz must contain at least one question.")

    def __len__(self) -> int:
        """Return the number of questions in the quiz."""
        return len(self.questions)

    def get_question(self, index: int) -> Question:
        """Return a question at the given index."""
        try:
            return self.questions[index]
        except IndexError as exc:
            raise IndexError(
                f"Question index out of range: {index}",
            ) from exc


@dataclass(slots=True)
class QuizSession:
    """Represent the state of an active quiz session."""

    quiz: Quiz
    current_index: int = 0
    score: int = 0
    answered_count: int = 0
    finished: bool = False

    @property
    def current_question(self) -> Question:
        """Return the question currently being displayed."""
        return self.quiz.get_question(self.current_index)

    @property
    def is_finished(self) -> bool:
        """Return whether the quiz session has finished."""
        return self.finished

    @property
    def total_questions(self) -> int:
        """Return the total number of questions in the quiz."""
        return len(self.quiz)

    @property
    def percentage(self) -> float:
        """Return the percentage of correctly answered questions."""
        if self.answered_count == 0:
            return 0.0

        return self.score / self.answered_count * 100

    def answer_current_question(self, answer: str) -> bool:
        """Answer the current question and return whether the answer is correct."""
        if self.is_finished:
            raise RuntimeError("The quiz session has already finished.")

        is_correct = answer == self.current_question.correct_answer

        if is_correct:
            self.score += 1

        self.answered_count += 1

        if self.answered_count == self.total_questions:
            self.finished = True

        return is_correct

    def next_question(self) -> None:
        """Move the session to the next question."""
        if self.is_finished:
            return

        self.current_index += 1


@dataclass(frozen=True, slots=True)
class QuestionView:
    """Represent question data prepared for presentation."""

    number: int
    total: int
    text: str
    answers: tuple[str, ...]
