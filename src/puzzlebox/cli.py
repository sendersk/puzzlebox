"""Command-line interface for PuzzleBox."""

from importlib.metadata import version
from pathlib import Path
from typing import Annotated

import typer

from puzzlebox.config import ConfigurationError, load_config
from puzzlebox.models import QuizSession
from puzzlebox.presentation import (
    display_answer_result,
    display_question,
    display_quiz_result,
    get_answer,
)
from puzzlebox.questions import QuestionLoadingError
from puzzlebox.quiz import create_quiz
from puzzlebox.repositories import JsonQuestionRepository
from puzzlebox.runner import QuizRunner


def get_version() -> str:
    """Return the installed PuzzleBox version."""
    return version("puzzlebox")


app = typer.Typer(
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def cli(
    questions: Annotated[
        Path | None,
        typer.Option(
            "--questions",
            "-q",
            help="Path to the JSON file containing quiz questions.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
    shuffle: bool | None = typer.Option(
        None,
        "--shuffle",
        help="Shuffle quiz questions before starting.",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        help="Show the PuzzleBox version and exit.",
    ),
) -> None:
    """Start the PuzzleBox quiz."""
    if version:
        typer.echo(f"PuzzleBox {get_version()}")
        raise typer.Exit()

    try:
        config = load_config(Path("config/settings.yaml"))
    except ConfigurationError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    questions_path = questions or config.questions_path
    shuffle_questions = (
        config.shuffle_questions
        if shuffle is None
        else shuffle
    )

    run_quiz(
        questions_path,
        shuffle_questions=shuffle_questions,
    )


def run_quiz(
    questions_path: Path,
    *,
    category: str | None = None,
    shuffle_questions: bool = False,
) -> None:
    """Run a quiz using the given question configuration."""
    try:
        runner = create_runner(
            questions_path,
            category=category,
            shuffle_questions=shuffle_questions,
        )
    except QuestionLoadingError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    print("PuzzleBox")
    print("=========")

    try:
        while not runner.is_finished:
            process_question(runner)
    except (KeyboardInterrupt, EOFError):
        typer.echo("\nQuiz cancelled.")
        return

    display_quiz_result(runner)


def process_question(runner: QuizRunner) -> None:
    """Process the current question."""
    display_question(runner)

    is_correct = answer_question(runner)

    display_answer_result(is_correct)
    move_to_next_question(runner)


def create_runner(
    questions_path: Path,
    *,
    category: str | None = None,
    shuffle_questions: bool = False,
) -> QuizRunner:
    """Create a quiz runner using the given question configuration."""
    repository = JsonQuestionRepository(questions_path)
    quiz = create_quiz(
        repository,
        category=category,
        shuffle=shuffle_questions,
    )
    return QuizRunner(QuizSession(quiz))


def answer_question(runner: QuizRunner) -> bool:
    """Answer the current question and return whether the answer is correct."""
    answer_number = get_answer(runner)
    answer = runner.current_question.answers[answer_number - 1]

    return runner.answer(answer)


def move_to_next_question(runner: QuizRunner) -> None:
    """Move to the next question when the quiz is not finished."""
    if not runner.is_finished:
        runner.next_question()
