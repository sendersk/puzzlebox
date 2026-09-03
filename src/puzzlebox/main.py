from puzzlebox.cli import app
from puzzlebox.logging import configure_logging


def main() -> None:
    """Start the PuzzleBox command-line application."""
    configure_logging()
    app()


if __name__ == "__main__":
    main()
