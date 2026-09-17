from pathlib import Path

import pytest
from pydantic import ValidationError

from puzzlebox.config import AppConfig, ConfigurationError, load_config


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
    """Test that unknown configuration fields raise an error."""
    config_path = tmp_path / "settings.yaml"

    config_path.write_text(
        "questions_path: questions.json\nunknown_setting: true\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Invalid configuration"):
        load_config(config_path)


def test_load_config_raises_error_when_file_is_missing(
    tmp_path: Path,
) -> None:
    """Test that a missing configuration file raises an error."""
    config_path = tmp_path / "missing.yaml"

    with pytest.raises(ConfigurationError, match="Unable to read"):
        load_config(config_path)


def test_load_config_rejects_invalid_yaml(tmp_path: Path) -> None:
    """Test that invalid YAML raises a configuration error."""
    config_path = tmp_path / "settings.yaml"

    config_path.write_text(
        "questions_path: [invalid",
        encoding="utf-8",
    )

    with pytest.raises(ConfigurationError, match="Invalid YAML"):
        load_config(config_path)


def test_app_config_shuffle_questions_defaults_to_false() -> None:
    """Test that question shuffling is disabled by default."""
    config = AppConfig()

    assert config.shuffle_questions is False


def test_load_config_reads_shuffle_questions(tmp_path: Path) -> None:
    """Test that question shuffling is loaded from YAML configuration."""
    config_path = tmp_path / "settings.yaml"
    config_path.write_text(
        """
questions_path: resources/questions.json
shuffle_questions: true
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.shuffle_questions is True


def test_load_config_defaults_shuffle_questions_when_missing(
    tmp_path: Path,
) -> None:
    """Test that missing shuffle configuration uses the default value."""
    config_path = tmp_path / "settings.yaml"
    config_path.write_text(
        "questions_path: resources/questions.json",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.shuffle_questions is False


def test_load_config_reads_category(tmp_path: Path) -> None:
    """Test that the category is loaded from configuration."""
    config_path = tmp_path / "settings.yaml"
    config_path.write_text(
        """
questions_path: resources/questions.json
shuffle_questions: false
category: Science
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.category == "Science"


def test_load_config_defaults_category_to_none(tmp_path: Path) -> None:
    """Test that category defaults to None when omitted."""
    config_path = tmp_path / "settings.yaml"
    config_path.write_text(
        """
questions_path: resources/questions.json
shuffle_questions: false
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.category is None