"""Application configuration entry point."""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError


class ConfigurationError(Exception):
    """Raised when application configuration cannot be loaded."""


class AppConfig(BaseModel):
    """Application configuration."""

    model_config = ConfigDict(extra="forbid")

    questions_path: Path = Path("resources/questions.json")


def load_config(path: Path) -> AppConfig:
    """Load application configuration from a YAML file."""
    try:
        with path.open("r", encoding="utf-8") as file:
            data = yaml.safe_load(file)

        if data is None:
            data = {}

        return AppConfig.model_validate(data)

    except OSError as exc:
        raise ConfigurationError(f"Unable to read configuration file: {path}") from exc

    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML in configuration file: {path}") from exc

    except ValidationError as exc:
        raise ConfigurationError(f"Invalid configuration data in: {path}") from exc
