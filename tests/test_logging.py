import logging

from puzzlebox.logging import configure_logging


def test_configure_logging_sets_root_log_level() -> None:
    """Test that logging is configured with the requested root level."""
    configure_logging(logging.DEBUG)

    root_logger = logging.getLogger()

    assert root_logger.level == logging.DEBUG


def test_configure_logging_emits_messages(caplog) -> None:
    """Test that configured logging captures application messages."""
    configure_logging(logging.INFO)

    logger = logging.getLogger("puzzlebox.test")

    with caplog.at_level(logging.INFO, logger="puzzlebox.test"):
        logger.info("Test message")

    assert "Test message" in caplog.text
