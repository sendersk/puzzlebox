"""Command-line interface for PuzzleBox."""

from pathlib import Path
from typing import Annotated

import typer

from puzzlebox.config import load_config
from puzzlebox.models import QuizSession
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
    config = load_config(Path("config/settings.yaml"))

    questions_path = questions or config.questions_path

    run_quiz(questions_path)


def run_quiz(questions_path: Path) -> None:
    """Run a quiz using questions from the given JSON file."""
    repository = JsonQuestionRepository(questions_path)
    quiz = create_quiz(repository)
    runner = QuizRunner(QuizSession(quiz))

    print("PuzzleBox")
    print("=========")

    while not runner.is_finished:
        process_question(runner)

    print()
    print("Quiz finished!")
    print(f"Score: {runner.score}/{runner.current_question.total}")
    print(f"Percentage: {runner.percentage:.1f}%")


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


def get_answer(question: QuizRunner) -> int:
    """Read an answer number from the user."""
    while True:
        value = input("Your answer: ")

        try:
            answer_number = int(value)
        except ValueError:
            print("Please enter a number.")
            continue

        if 1 <= answer_number <= len(question.current_question.answers):
            return answer_number

        print("Please select one of the available answers.")


def process_question(runner: QuizRunner) -> None:
    """Process the current question."""
    display_question(runner)

    answer_number = get_answer(runner)
    answer = runner.current_question.answers[answer_number - 1]

    is_correct = runner.answer(answer)

    if is_correct:
        print("Correct!")
    else:
        print("Wrong!")

    if not runner.is_finished:
        runner.next_question()
