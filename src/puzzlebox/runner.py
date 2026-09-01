"""Quiz execution logic."""

from puzzlebox.models import QuestionView, QuizSession


class QuizRunner:
    """Run a quiz session using an input/output interface."""

    def __init__(self, session: QuizSession) -> None:
        self._session = session

    def answer(self, answer: str) -> bool:
        """Submit an answer for the current question."""
        return self._session.answer_current_question(answer)

    def next_question(self) -> None:
        """Move to the next question."""
        self._session.next_question()

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
