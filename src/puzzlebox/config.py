"""Application configuration entry point."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict


class AppConfig(BaseModel):
    """Application configuration."""

    model_config = ConfigDict(extra="forbid")

    questions_path: Path = Path("resources/questions.json")
