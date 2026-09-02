from pathlib import Path

import pytest
from pydantic import ValidationError

from puzzlebox.config import AppConfig, load_config


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


def test_load_config(tmp_path: Path) -> None:
    """Test that configuration is loaded from a YAML file."""
    config_path = tmp_path / "settings.yaml"

    config_path.write_text(
        "questions_path: custom/questions.json\n",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.questions_path == Path("custom/questions.json")


def test_load_config_uses_defaults_for_empty_file(tmp_path: Path) -> None:
    """Test that an empty configuration uses default values."""
    config_path = tmp_path / "settings.yaml"
    config_path.write_text("", encoding="utf-8")

    config = load_config(config_path)

    assert config.questions_path == Path("resources/questions.json")


def test_load_config_rejects_unknown_fields(tmp_path: Path) -> None:
    """Test that unknown YAML fields are rejected."""
    config_path = tmp_path / "settings.yaml"

    config_path.write_text(
        "questions_path: questions.json\nunknown_setting: true\n",
        encoding="utf-8",
    )

    with pytest.raises(ValidationError):
        load_config(config_path)
