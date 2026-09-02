"""PuzzleBox application entry point."""

from pathlib import Path

from puzzlebox.cli import run_quiz


def main() -> None:
    """Run the PuzzleBox application."""
    questions_path = Path("resources/questions.json")
    run_quiz(questions_path)


if __name__ == "__main__":
    main()
