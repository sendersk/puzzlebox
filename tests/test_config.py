from pathlib import Path

import pytest
from pydantic import ValidationError

from puzzlebox.config import AppConfig


def test_config_uses_default_questions_path() -> None:
    """Test that the default questions path is configured correctly."""
    config = AppConfig()

    assert config.questions_path == Path("resources/questions.json")


def test_config_accepts_custom_questions_path() -> None:
    """Test that a custom questions path can be configured."""
    path = Path("data/questions.json")

    config = AppConfig(questions_path=path)

    assert config.questions_path == path


def test_config_rejects_unknown_fields() -> None:
    """Test that unknown configuration fields are rejected."""
    with pytest.raises(ValidationError):
        AppConfig(
            questions_path=Path("questions.json"),
            unknown_setting="value",
        )
