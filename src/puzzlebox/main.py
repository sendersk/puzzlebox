import logging

from puzzlebox.cli import app
from puzzlebox.logging import configure_logging

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the PuzzleBox command-line application."""
    configure_logging()

    logger.info("PuzzleBox started")

    app()


if __name__ == "__main__":
    main()
