"""Application configuration entry point."""

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict


class AppConfig(BaseModel):
    """Application configuration."""

    model_config = ConfigDict(extra="forbid")

    questions_path: Path = Path("resources/questions.json")


def load_config(path: Path) -> AppConfig:
    """Load application configuration from a YAML file."""
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if data is None:
        data = {}

    return AppConfig.model_validate(data)
