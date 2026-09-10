"""Presentation helpers for the PuzzleBox CLI."""

from puzzlebox.runner import QuizRunner


def display_question(runner: QuizRunner) -> None:
    """Display the current question."""
    question = runner.current_question

    print()
    print(f"Question {question.number}/{question.total}")
    print()
    print(question.text)
    print()

    for number, answer in enumerate(question.answers, start=1):
        print(f"{number}. {answer}")
