"""Command-line interface for PuzzleBox."""

from pathlib import Path
from typing import Annotated

import typer

from puzzlebox.config import ConfigurationError, load_config
from puzzlebox.models import QuizSession
from puzzlebox.presentation import display_answer_result, display_question, display_quiz_result, get_answer
from puzzlebox.questions import QuestionLoadingError
from puzzlebox.quiz import create_quiz
from puzzlebox.repositories import JsonQuestionRepository
from puzzlebox.runner import QuizRunner

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
) -> None:
    """Start the PuzzleBox quiz."""
    try:
        config = load_config(Path("config/settings.yaml"))
    except ConfigurationError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    questions_path = questions or config.questions_path

    run_quiz(questions_path)


def run_quiz(questions_path: Path) -> None:
    """Run a quiz using questions from the given JSON file."""
    try:
        runner = create_runner(questions_path)
    except QuestionLoadingError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    print("PuzzleBox")
    print("=========")

    while not runner.is_finished:
        process_question(runner)

    display_quiz_result(runner)

def process_question(runner: QuizRunner) -> None:
    """Process the current question."""
    display_question(runner)

    answer_number = get_answer(runner)
    answer = runner.current_question.answers[answer_number - 1]

    is_correct = runner.answer(answer)

    display_answer_result(is_correct)

    if not runner.is_finished:
        runner.next_question()


def create_runner(questions_path: Path) -> QuizRunner:
    """Create a quiz runner using questions from the given JSON file."""
    repository = JsonQuestionRepository(questions_path)
    quiz = create_quiz(repository)

    return QuizRunner(QuizSession(quiz))
