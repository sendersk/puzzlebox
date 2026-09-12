"""Quiz execution logic."""

import logging
from dataclasses import dataclass

from puzzlebox.models import QuizSession

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class QuestionView:
    """Represent question data prepared for presentation."""

    number: int
    total: int
    text: str
    answers: tuple[str, ...]


class QuizRunner:
    """Run a quiz session using an input/output interface."""

    def __init__(self, session: QuizSession) -> None:
        self._session = session

    @property
    def current_question(self) -> QuestionView:
        """Return the current question prepared for presentation."""
        question = self._session.current_question

        return QuestionView(
            number=self._session.current_index + 1,
            total=self._session.total_questions,
            text=question.text,
            answers=question.answers,
        )

    @property
    def is_finished(self) -> bool:
        """Return whether the current quiz session has finished."""
        return self._session.is_finished

    @property
    def score(self) -> int:
        """Return the current score."""
        return self._session.score

    @property
    def percentage(self) -> float:
        """Return the current percentage."""
        return self._session.percentage

    @property
    def total_questions(self) -> int:
        """Return the total number of questions."""
        return self._session.total_questions

    def answer(self, answer: str) -> bool:
        """Answer the current question."""
        is_correct = self._session.answer_current_question(answer)

        logger.info(
            "Question answered: %s",
            "correct" if is_correct else "incorrect",
        )

        if self.is_finished:
            logger.info(
                "Quiz finished: score=%d/%d (%.1f%%)",
                self.score,
                self.total_questions,
                self.percentage,
            )

        return is_correct

    def next_question(self) -> None:
        """Move to the next question."""
        self._session.next_question()
